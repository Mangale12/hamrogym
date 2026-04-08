from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.timezone import localdate
from django.views.generic import TemplateView

from ..models import Asset


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
        today = localdate()
        for item in assignment_history:
            item.is_overdue = bool(
                item.status == "active"
                and item.expected_return_date
                and item.expected_return_date < today
            )
        maintenance_records = asset.maintenance_records.select_related(
            "incident__incident_type",
            "vendor",
            "performed_by",
        ).all()
        transfer_history = asset.transfers.select_related(
            "from_location",
            "to_location",
            "from_department",
            "to_department",
            "transferred_by",
            "received_by",
        ).all()
        documents = asset.assetdocument_set.all()

        context.update(
            {
                "asset": asset,
                "assignment_history": assignment_history,
                "maintenance_records": maintenance_records,
                "transfer_history": transfer_history,
                "documents": documents,
                "active_assignment": next(
                    (item for item in assignment_history if item.status == "active" and not item.return_date),
                    None,
                ),
                "has_overdue_assignment": any(item.is_overdue for item in assignment_history),
            }
        )
        return context
