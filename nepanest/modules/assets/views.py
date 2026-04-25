from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import TemplateView

from nepanest.common.helpers.context import get_current_branch_id, get_current_fiscal_year_id
from nepanest.foundation.fiscal import FiscalYear
from nepanest.foundation.organization import Branch

from .models import Asset
from .services import (
    generate_monthly_depreciation_schedule,
    parse_schedule_month_value,
    post_monthly_depreciation_entries,
)


def _resolve_active_depreciation_context(request):
    branch_id = get_current_branch_id(request)
    fiscal_year_id = get_current_fiscal_year_id(request)

    branch = Branch.objects.select_related("organization").filter(pk=branch_id).first() if branch_id else None
    fiscal_year = FiscalYear.objects.filter(pk=fiscal_year_id).first() if fiscal_year_id else None

    if not branch:
        raise ValidationError("Active branch is required in session to process depreciation.")
    if not fiscal_year:
        raise ValidationError("Active fiscal year is required in session to process depreciation.")

    return {
        "branch": branch,
        "organization": branch.organization,
        "fiscal_year": fiscal_year,
    }


def _build_summary_message(prefix: str, summary: dict) -> str:
    message = (
        f"{prefix} for {summary['month_label']}. "
        f"Processed assets: {summary.get('assets_processed', 0)}/{summary.get('assets_considered', 0)}. "
        if "assets_considered" in summary
        else (
            f"{prefix} for {summary['month_label']}. "
            f"Posted entries: {summary.get('posted', 0)}/{summary.get('unposted_entries', 0)}. "
        )
    )

    if "created" in summary:
        message += (
            f"Created lines: {summary['created']}, Updated lines: {summary['updated']}, "
            f"Skipped posted lines: {summary['skipped']}, Not due assets: {summary['not_due']}."
        )
    else:
        message += (
            f"Already posted: {summary['already_posted']}, Remaining unposted: {summary['remaining_unposted']}, "
            f"Total amount: {summary['total_amount']:.2f}."
        )

    if summary.get("error_count"):
        sample_errors = "; ".join(summary["errors"][:3])
        message += f" Setup/posting issues: {summary['error_count']}."
        if sample_errors:
            message += f" Examples: {sample_errors}"

    return message


class MonthlyDepreciationRunView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            active_context = _resolve_active_depreciation_context(request)
            schedule_month = parse_schedule_month_value(request.POST.get("schedule_month"))
            summary = generate_monthly_depreciation_schedule(
                schedule_month=schedule_month,
                organization=active_context["organization"],
                branch=active_context["branch"],
                fiscal_year=active_context["fiscal_year"],
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": _build_summary_message("Monthly depreciation schedule generated", summary),
                    "summary": summary,
                }
            )
        except ValidationError as exc:
            if hasattr(exc, "message_dict"):
                message = " ".join(
                    " ".join(messages) if isinstance(messages, list) else str(messages)
                    for messages in exc.message_dict.values()
                ).strip() or "Monthly depreciation run failed."
                return JsonResponse({"success": False, "message": message, "errors": exc.message_dict}, status=400)

            messages = exc.messages if hasattr(exc, "messages") else [str(exc)]
            message = " ".join(str(item) for item in messages if item).strip() or "Monthly depreciation run failed."
            return JsonResponse({"success": False, "message": message}, status=400)


class MonthlyDepreciationPostView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            active_context = _resolve_active_depreciation_context(request)
            schedule_month = parse_schedule_month_value(request.POST.get("schedule_month"))
            summary = post_monthly_depreciation_entries(
                schedule_month=schedule_month,
                branch=active_context["branch"],
                fiscal_year=active_context["fiscal_year"],
                user=request.user,
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": _build_summary_message("Monthly depreciation posting completed", summary),
                    "summary": summary,
                }
            )
        except ValidationError as exc:
            if hasattr(exc, "message_dict"):
                message = " ".join(
                    " ".join(messages) if isinstance(messages, list) else str(messages)
                    for messages in exc.message_dict.values()
                ).strip() or "Monthly depreciation posting failed."
                return JsonResponse({"success": False, "message": message, "errors": exc.message_dict}, status=400)

            messages = exc.messages if hasattr(exc, "messages") else [str(exc)]
            message = " ".join(str(item) for item in messages if item).strip() or "Monthly depreciation posting failed."
            return JsonResponse({"success": False, "message": message}, status=400)


class AssetProfileView(LoginRequiredMixin, TemplateView):
    template_name = "assets/asset_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset = get_object_or_404(
            Asset.objects.select_related(
                "category",
                "asset_type",
                "brand",
                "vendor",
                "current_location",
                "current_department",
                "current_employee",
                "status",
                "condition",
            ),
            pk=self.kwargs["pk"],
        )
        assignment_history = asset.assignments.select_related(
            "employee__user",
            "assigned_by",
            "received_by",
            "condition_at_issue",
            "condition_at_return",
        ).all()
        maintenance_records = asset.maintenance_records.select_related(
            "vendor",
            "performed_by",
        ).all()
        documents = asset.assetdocument_set.all()

        context.update(
            {
                "asset": asset,
                "assignment_history": assignment_history,
                "maintenance_records": maintenance_records,
                "documents": documents,
                "active_assignment": next((item for item in assignment_history if item.status == "active" and not item.return_date), None),
            }
        )
        return context
