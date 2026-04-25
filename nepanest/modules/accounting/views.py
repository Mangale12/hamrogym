from collections import defaultdict
from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from core.registry import get_entity_config
from core.views.entities import _build_entity_form, _resolve_field_urls, _serialize_form_instance
from core.views.reports import BaseReportView
from nepanest.common.helpers.context import get_current_branch_id, get_current_fiscal_year_id
from nepanest.foundation.fiscal import FiscalYear
from nepanest.foundation.organization import Branch

from .forms import (
    BalanceSheetReportForm,
    CashFlowReportForm,
    DayBookReportForm,
    DepreciationEffectReportForm,
    GeneralLedgerReportForm,
    ProfitLossReportForm,
    SpecialBookReportForm,
    TrialBalanceReportForm,
)
from .models import ChartOfAccount
from .services import (
    build_balance_sheet_report,
    build_cash_flow_report,
    build_day_book_report,
    build_depreciation_effect_report,
    build_general_ledger_report,
    build_profit_loss_report,
    build_special_book_report,
    build_trial_balance_report,
)


class ChartParentSelectView(LoginRequiredMixin, View):
    def get(self, request):
        term = (request.GET.get("term") or request.GET.get("q") or "").strip()
        ids_param = (request.GET.get("ids") or request.GET.get("id") or "").strip()

        queryset = ChartOfAccount.objects.filter(is_ledger=False).order_by("code", "name")

        if ids_param:
            ids = [int(val) for val in ids_param.split(",") if val.strip().isdigit()]
            items = list(queryset.filter(pk__in=ids))
            return JsonResponse(
                {
                    "results": [
                        {
                            "id": obj.pk,
                            "text": f"{obj.code or 'AUTO'} - {obj.name}",
                            "depth": max((obj.report_level or 1) - 1, 0),
                            "path": obj.full_path,
                        }
                        for obj in items
                    ],
                    "pagination": {"more": False},
                }
            )

        if term:
            queryset = queryset.filter(
                Q(code__icontains=term)
                | Q(name__icontains=term)
                | Q(parent__name__icontains=term)
                | Q(parent__code__icontains=term)
            )

        page = max(int(request.GET.get("page", 1)), 1)
        page_size = 20
        start = (page - 1) * page_size
        items = list(queryset[start : start + page_size + 1])
        more = len(items) > page_size
        items = items[:page_size]

        return JsonResponse(
            {
                "results": [
                    {
                        "id": obj.pk,
                        "text": f"{obj.code or 'AUTO'} - {obj.name}",
                        "depth": max((obj.report_level or 1) - 1, 0),
                        "path": obj.full_path,
                    }
                    for obj in items
                ],
                "pagination": {"more": more},
            }
        )


class LedgerAccountSelectView(LoginRequiredMixin, View):
    def get(self, request):
        term = (request.GET.get("term") or request.GET.get("q") or "").strip()
        ids_param = (request.GET.get("ids") or request.GET.get("id") or "").strip()

        queryset = (
            ChartOfAccount.objects.filter(is_ledger=True)
            .select_related("parent")
            .order_by("code", "name")
        )

        if ids_param:
            ids = [int(val) for val in ids_param.split(",") if val.strip().isdigit()]
            items = list(queryset.filter(pk__in=ids))
            return JsonResponse(
                {
                    "results": [{"id": obj.pk, "text": f"{obj.code or 'AUTO'} - {obj.full_path}"} for obj in items],
                    "pagination": {"more": False},
                }
            )

        if term:
            queryset = queryset.filter(
                Q(code__icontains=term)
                | Q(name__icontains=term)
                | Q(parent__name__icontains=term)
                | Q(parent__code__icontains=term)
                | Q(ledger_profile__pan_no__icontains=term)
                | Q(ledger_profile__vat_no__icontains=term)
            )

        page = max(int(request.GET.get("page", 1)), 1)
        page_size = 20
        start = (page - 1) * page_size
        items = list(queryset[start : start + page_size + 1])
        more = len(items) > page_size
        items = items[:page_size]

        return JsonResponse(
            {
                "results": [{"id": obj.pk, "text": f"{obj.code or 'AUTO'} - {obj.full_path}"} for obj in items],
                "pagination": {"more": more},
            }
        )


class JournalRootAccountSelectView(LoginRequiredMixin, View):
    def get(self, request):
        term = (request.GET.get("term") or request.GET.get("q") or "").strip()
        ids_param = (request.GET.get("ids") or request.GET.get("id") or "").strip()

        queryset = (
            ChartOfAccount.objects.filter(is_ledger=False, parent__isnull=True, is_active=True)
            .order_by("code", "name")
        )

        if ids_param:
            ids = [int(val) for val in ids_param.split(",") if val.strip().isdigit()]
            items = list(queryset.filter(pk__in=ids))
            return JsonResponse(
                {
                    "results": [{"id": obj.pk, "text": f"{obj.code or 'AUTO'} - {obj.name}"} for obj in items],
                    "pagination": {"more": False},
                }
            )

        if term:
            queryset = queryset.filter(Q(code__icontains=term) | Q(name__icontains=term))

        page = max(int(request.GET.get("page", 1)), 1)
        page_size = 20
        start = (page - 1) * page_size
        items = list(queryset[start : start + page_size + 1])
        more = len(items) > page_size
        items = items[:page_size]

        return JsonResponse(
            {
                "results": [{"id": obj.pk, "text": f"{obj.code or 'AUTO'} - {obj.name}"} for obj in items],
                "pagination": {"more": more},
            }
        )


class JournalLedgerAccountSelectView(LoginRequiredMixin, View):
    def get(self, request):
        term = (request.GET.get("term") or request.GET.get("q") or "").strip()
        ids_param = (request.GET.get("ids") or request.GET.get("id") or "").strip()
        root_id = request.GET.get("root_id")

        queryset = (
            ChartOfAccount.objects.filter(is_ledger=True, is_active=True)
            .select_related("parent")
            .order_by("code", "name")
        )

        if root_id and str(root_id).isdigit():
            root = ChartOfAccount.objects.filter(pk=int(root_id), is_ledger=False).first()
            if root:
                queryset = queryset.filter(account_type=root.account_type)

        if ids_param:
            ids = [int(val) for val in ids_param.split(",") if val.strip().isdigit()]
            items = list(queryset.filter(pk__in=ids))
            return JsonResponse(
                {
                    "results": [{"id": obj.pk, "text": f"{obj.code or 'AUTO'} - {obj.full_path}"} for obj in items],
                    "pagination": {"more": False},
                }
            )

        if term:
            queryset = queryset.filter(
                Q(code__icontains=term)
                | Q(name__icontains=term)
                | Q(parent__name__icontains=term)
                | Q(parent__code__icontains=term)
                | Q(ledger_profile__pan_no__icontains=term)
                | Q(ledger_profile__vat_no__icontains=term)
            )

        page = max(int(request.GET.get("page", 1)), 1)
        page_size = 20
        start = (page - 1) * page_size
        items = list(queryset[start : start + page_size + 1])
        more = len(items) > page_size
        items = items[:page_size]

        return JsonResponse(
            {
                "results": [{"id": obj.pk, "text": f"{obj.code or 'AUTO'} - {obj.full_path}"} for obj in items],
                "pagination": {"more": more},
            }
        )


def _build_account_tree(queryset, *, entity_name):
    children_map = defaultdict(list)
    root_nodes = []

    for account in queryset:
        account.child_nodes = []
        children_map[account.parent_id].append(account)

    for account in queryset:
        account.child_nodes = children_map.get(account.pk, [])
        account.child_count = len(account.child_nodes)
        account.is_group = account.child_count > 0
        try:
            account.ledger_info = account.ledger_profile
        except Exception:
            account.ledger_info = None
        account.detail_url = reverse(f"{entity_name}_detail", args=[account.pk])
        account.delete_url = reverse(f"{entity_name}_delete", args=[account.pk])
        if account.parent_id is None:
            root_nodes.append(account)

    return root_nodes


class ChartOfAccountTreeView(LoginRequiredMixin, TemplateView):
    template_name = "account/chart_of_account_tree.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = get_entity_config("chart_of_account")
        fields = _resolve_field_urls(entity.fields, self.request)
        form_defaults = _serialize_form_instance(_build_entity_form(entity, request=self.request), self.request)

        queryset = entity.model.objects.filter(is_ledger=False).select_related(
            "parent",
            "organization",
            "branch",
            "fiscal_year",
        ).order_by("code", "sort_order", "id")

        root_nodes = _build_account_tree(queryset, entity_name=entity.name)

        context.update(
            {
                "entity_name": entity.name,
                "entity_label": entity.verbose_name,
                "modal_id": f"{entity.name}Modal",
                "form_id": f"{entity.name}Form",
                "fields": fields,
                "tree_roots": root_nodes,
                "create_url": reverse(f"{entity.name}_create"),
                "update_url_template": reverse(f"{entity.name}_update", args=[0]).replace("/0/", "/{id}/"),
                "detail_url_template": reverse(f"{entity.name}_detail", args=[0]).replace("/0/", "/{id}/"),
                "delete_url_template": reverse(f"{entity.name}_delete", args=[0]).replace("/0/", "/{id}/"),
                "modal_title_add": f"Add {entity.verbose_name}",
                "modal_title_edit": f"Edit {entity.verbose_name}",
                "reset_defaults": {**form_defaults, **(entity.reset_defaults or {})},
                "summary": {
                    "total": queryset.count(),
                    "groups": len(root_nodes),
                    "postable": entity.model.objects.filter(is_ledger=True).count(),
                    "depreciation": queryset.filter(is_depreciation=True).count(),
                },
            }
        )
        return context


class FinancialStatementViewMixin:
    def get_active_reporting_scope(self):
        branch = None
        branch_id = get_current_branch_id(self.request)
        if branch_id:
            branch = Branch.objects.select_related("organization").filter(pk=branch_id).first()

        fiscal_year = None
        fiscal_year_id = get_current_fiscal_year_id(self.request)
        if fiscal_year_id:
            fiscal_year = FiscalYear.objects.filter(pk=fiscal_year_id).first()

        organization = branch.organization if branch else None
        return {
            "organization": organization,
            "branch": branch,
            "fiscal_year": fiscal_year,
        }

    def get_default_reporting_dates(self):
        scope = self.get_active_reporting_scope()
        fiscal_year = scope["fiscal_year"]
        today = timezone.localdate()
        default_end = fiscal_year.end_date if fiscal_year and fiscal_year.end_date < today else today
        default_start = fiscal_year.start_date if fiscal_year else today.replace(month=1, day=1)
        return {
            **scope,
            "default_start": default_start,
            "default_end": default_end,
        }

    def build_report_link(self, url_name: str, **params):
        normalized = {}
        for key, value in params.items():
            if value in (None, "", False):
                continue
            normalized[key] = value.pk if hasattr(value, "pk") else value
        query = urlencode(normalized)
        base_url = reverse(url_name)
        return f"{base_url}?{query}" if query else base_url

    def build_custom_ajax_payload(self, *, form, report_data, results_template: str):
        context = self.get_report_context(
            form=form,
            report_data=report_data,
            export_query=self.get_export_query() if report_data else "",
        )
        return {
            "success": form.is_valid(),
            "form_html": render_to_string(
                "components/report/report_filters_panel.html",
                context,
                request=self.request,
            ),
            "results_html": render_to_string(
                results_template,
                context,
                request=self.request,
            ),
        }

    def get_filter_blocks(self):
        resolved_blocks = []
        for block in super().get_filter_blocks():
            block_data = dict(block)
            block_data["fields"] = _resolve_field_urls(block_data.get("fields", []), self.request)
            resolved_blocks.append(block_data)
        return resolved_blocks


class BalanceSheetReportView(FinancialStatementViewMixin, BaseReportView):
    template_name = "account/balance_sheet_report.html"
    form_class = BalanceSheetReportForm
    report_title = "Balance Sheet"
    export_filename = "balance_sheet"
    report_table_id = "balanceSheetExportTable"
    print_settings = {
        "page_size": "A4",
        "orientation": "landscape",
        "margin": "8mm",
        "summary_columns": 3,
    }
    export_columns = [
        ("section", "Section"),
        ("code", "Code"),
        ("account", "Account"),
        ("level", "Level"),
        ("account_kind", "Type"),
        ("amount", "Amount"),
    ]
    filter_blocks = [
        {
            "title": "Primary Filters",
            "description": "Build an as-of balance sheet across assets, liabilities, equity, and current-period earnings.",
            "fields": [
                {"name": "organization", "label": "Organization", "col": "col-md-3", "url_name": "organization_select"},
                {"name": "branch", "label": "Branch", "col": "col-md-3", "url_name": "branch_select"},
                {"name": "fiscal_year", "label": "Fiscal Year", "col": "col-md-3", "url_name": "fiscal_year_select"},
                {"name": "as_of_date", "label": "As Of Date", "col": "col-md-3", "calendar_switchable": True},
            ],
        },
        {
            "advanced": True,
            "title": "Display Options",
            "fields": [
                {"name": "show_zero_balances", "label": "Show Zero Balances", "col": "col-md-3", "type": "checkbox"},
            ],
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        },
    ]

    def get_initial_filters(self):
        defaults = self.get_default_reporting_dates()
        return {
            "organization": defaults["organization"],
            "branch": defaults["branch"],
            "fiscal_year": defaults["fiscal_year"],
            "as_of_date": defaults["default_end"],
            "show_zero_balances": False,
        }

    def get_form(self):
        return self.form_class(self.get_form_data(), initial=self.get_initial_filters())

    def get_export_columns(self):
        return list(self.export_columns)

    def get_table_rows(self, report_data):
        return list((report_data or {}).get("rows", []))

    def get_report_subtitle(self, report_data=None):
        if report_data:
            pieces = [f"As of {report_data['as_of_date']}"]
            if report_data.get("fiscal_year"):
                pieces.append(f"Fiscal Year: {report_data['fiscal_year']}")
            if report_data.get("branch"):
                pieces.append(f"Branch: {report_data['branch']}")
            elif report_data.get("organization"):
                pieces.append(f"Organization: {report_data['organization']}")
            return " | ".join(pieces)
        return "Review balance-sheet heads with current-period earnings folded into equity."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Assets", "value": summary.get("total_assets", 0)},
            {"label": "Liabilities", "value": summary.get("total_liabilities", 0)},
            {"label": "Equity", "value": summary.get("total_equity", 0)},
            {"label": "Current Earnings", "value": summary.get("current_earnings", 0)},
            {"label": "Liabilities + Equity", "value": summary.get("total_liabilities_and_equity", 0)},
            {"label": "Difference", "value": summary.get("difference", 0)},
        ]

    def build_report_data(self, cleaned_data):
        fiscal_year = cleaned_data.get("fiscal_year")
        as_of_date = cleaned_data.get("as_of_date")
        profit_loss_start = fiscal_year.start_date if fiscal_year else as_of_date.replace(month=1, day=1)
        report_data = build_balance_sheet_report(
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=fiscal_year,
            as_of_date=as_of_date,
            show_zero_balances=bool(cleaned_data.get("show_zero_balances")),
        )
        report_data["profit_loss_url"] = self.build_report_link(
            "profit_loss_report",
            generate=1,
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=fiscal_year,
            date_from=profit_loss_start,
            date_to=as_of_date,
        )
        return report_data

    def build_ajax_payload(self, *, form, report_data):
        return self.build_custom_ajax_payload(
            form=form,
            report_data=report_data,
            results_template="account/partials/balance_sheet_report_results.html",
        )


class ProfitLossReportView(FinancialStatementViewMixin, BaseReportView):
    template_name = "account/profit_loss_report.html"
    form_class = ProfitLossReportForm
    report_title = "Profit & Loss Statement"
    export_filename = "profit_loss_statement"
    report_table_id = "profitLossExportTable"
    print_settings = {
        "page_size": "A4",
        "orientation": "landscape",
        "margin": "8mm",
        "summary_columns": 3,
    }
    export_columns = [
        ("section", "Section"),
        ("code", "Code"),
        ("account", "Account"),
        ("level", "Level"),
        ("account_kind", "Type"),
        ("amount", "Amount"),
    ]
    filter_blocks = [
        {
            "title": "Primary Filters",
            "description": "Build an ERP-style income statement for a specific reporting period.",
            "fields": [
                {"name": "organization", "label": "Organization", "col": "col-md-3", "url_name": "organization_select"},
                {"name": "branch", "label": "Branch", "col": "col-md-3", "url_name": "branch_select"},
                {"name": "fiscal_year", "label": "Fiscal Year", "col": "col-md-2", "url_name": "fiscal_year_select"},
                {"name": "date_from", "label": "Date From", "col": "col-md-2", "calendar_switchable": True},
                {"name": "date_to", "label": "Date To", "col": "col-md-2", "calendar_switchable": True},
            ],
        },
        {
            "advanced": True,
            "title": "Display Options",
            "fields": [
                {"name": "show_zero_balances", "label": "Show Zero Balances", "col": "col-md-3", "type": "checkbox"},
            ],
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        },
    ]

    def get_initial_filters(self):
        defaults = self.get_default_reporting_dates()
        return {
            "organization": defaults["organization"],
            "branch": defaults["branch"],
            "fiscal_year": defaults["fiscal_year"],
            "date_from": defaults["default_start"],
            "date_to": defaults["default_end"],
            "show_zero_balances": False,
        }

    def get_form(self):
        return self.form_class(self.get_form_data(), initial=self.get_initial_filters())

    def get_export_columns(self):
        return list(self.export_columns)

    def get_table_rows(self, report_data):
        return list((report_data or {}).get("rows", []))

    def get_report_subtitle(self, report_data=None):
        if report_data:
            pieces = [f"{report_data['date_from']} to {report_data['date_to']}"]
            if report_data.get("fiscal_year"):
                pieces.append(f"Fiscal Year: {report_data['fiscal_year']}")
            if report_data.get("branch"):
                pieces.append(f"Branch: {report_data['branch']}")
            elif report_data.get("organization"):
                pieces.append(f"Organization: {report_data['organization']}")
            return " | ".join(pieces)
        return "Review income, expense, and net result for the selected period."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Income", "value": summary.get("total_income", 0)},
            {"label": "Expenses", "value": summary.get("total_expenses", 0)},
            {"label": summary.get("net_result_label", "Net Result"), "value": summary.get("net_result", 0)},
        ]

    def build_report_data(self, cleaned_data):
        report_data = build_profit_loss_report(
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
            show_zero_balances=bool(cleaned_data.get("show_zero_balances")),
        )
        report_data["balance_sheet_url"] = self.build_report_link(
            "balance_sheet_report",
            generate=1,
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            as_of_date=cleaned_data.get("date_to"),
        )
        return report_data

    def build_ajax_payload(self, *, form, report_data):
        return self.build_custom_ajax_payload(
            form=form,
            report_data=report_data,
            results_template="account/partials/profit_loss_report_results.html",
        )


class CashFlowReportView(FinancialStatementViewMixin, BaseReportView):
    template_name = "account/cash_flow_report.html"
    form_class = CashFlowReportForm
    report_title = "Cash Flow Statement"
    export_filename = "cash_flow_statement"
    report_table_id = "cashFlowExportTable"
    print_settings = {
        "page_size": "A4",
        "orientation": "landscape",
        "margin": "8mm",
        "summary_columns": 3,
    }
    export_columns = [
        ("section", "Section"),
        ("code", "Code"),
        ("account", "Account"),
        ("flow_type", "Flow Type"),
        ("amount", "Amount"),
    ]
    filter_blocks = [
        {
            "title": "Primary Filters",
            "description": "Build a direct-method cash flow statement from posted cash and bank movements.",
            "fields": [
                {"name": "organization", "label": "Organization", "col": "col-md-3", "url_name": "organization_select"},
                {"name": "branch", "label": "Branch", "col": "col-md-3", "url_name": "branch_select"},
                {"name": "fiscal_year", "label": "Fiscal Year", "col": "col-md-2", "url_name": "fiscal_year_select"},
                {"name": "date_from", "label": "Date From", "col": "col-md-2", "calendar_switchable": True},
                {"name": "date_to", "label": "Date To", "col": "col-md-2", "calendar_switchable": True},
            ],
        },
        {
            "advanced": True,
            "title": "Display Options",
            "fields": [
                {"name": "show_zero_balances", "label": "Show Zero Balances", "col": "col-md-3", "type": "checkbox"},
            ],
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        },
    ]

    def get_initial_filters(self):
        defaults = self.get_default_reporting_dates()
        return {
            "organization": defaults["organization"],
            "branch": defaults["branch"],
            "fiscal_year": defaults["fiscal_year"],
            "date_from": defaults["default_start"],
            "date_to": defaults["default_end"],
            "show_zero_balances": False,
        }

    def get_form(self):
        return self.form_class(self.get_form_data(), initial=self.get_initial_filters())

    def get_export_columns(self):
        return list(self.export_columns)

    def get_table_rows(self, report_data):
        return list((report_data or {}).get("rows", []))

    def get_report_subtitle(self, report_data=None):
        if report_data:
            pieces = [
                f"{report_data['date_from']} to {report_data['date_to']}",
                f"Method: {report_data.get('method', 'Direct Method')}",
            ]
            if report_data.get("fiscal_year"):
                pieces.append(f"Fiscal Year: {report_data['fiscal_year']}")
            if report_data.get("branch"):
                pieces.append(f"Branch: {report_data['branch']}")
            elif report_data.get("organization"):
                pieces.append(f"Organization: {report_data['organization']}")
            return " | ".join(pieces)
        return "Review operating, investing, and financing cash movements with opening and closing cash balances."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Opening Cash", "value": summary.get("opening_cash", 0)},
            {"label": "Operating", "value": summary.get("net_cash_from_operating", 0)},
            {"label": "Investing", "value": summary.get("net_cash_from_investing", 0)},
            {"label": "Financing", "value": summary.get("net_cash_from_financing", 0)},
            {"label": "Net Change", "value": summary.get("net_change_in_cash", 0)},
            {"label": "Closing Cash", "value": summary.get("closing_cash", 0)},
        ]

    def build_report_data(self, cleaned_data):
        report_data = build_cash_flow_report(
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
            show_zero_balances=bool(cleaned_data.get("show_zero_balances")),
        )
        report_data["balance_sheet_url"] = self.build_report_link(
            "balance_sheet_report",
            generate=1,
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            as_of_date=cleaned_data.get("date_to"),
        )
        report_data["profit_loss_url"] = self.build_report_link(
            "profit_loss_report",
            generate=1,
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
        )
        return report_data

    def build_ajax_payload(self, *, form, report_data):
        return self.build_custom_ajax_payload(
            form=form,
            report_data=report_data,
            results_template="account/partials/cash_flow_report_results.html",
        )


class TrialBalanceReportView(FinancialStatementViewMixin, BaseReportView):
    template_name = "account/trial_balance_report.html"
    form_class = TrialBalanceReportForm
    report_title = "Trial Balance"
    export_filename = "trial_balance"
    report_table_id = "trialBalanceExportTable"
    print_settings = {
        "page_size": "A4",
        "orientation": "landscape",
        "margin": "8mm",
        "summary_columns": 3,
    }
    export_columns = [
        ("code", "Code"),
        ("account", "Account"),
        ("account_type", "Account Type"),
        ("level", "Level"),
        ("account_kind", "Type"),
        ("opening_debit", "Opening Debit"),
        ("opening_credit", "Opening Credit"),
        ("period_debit", "Period Debit"),
        ("period_credit", "Period Credit"),
        ("closing_debit", "Closing Debit"),
        ("closing_credit", "Closing Credit"),
    ]
    filter_blocks = [
        {
            "title": "Primary Filters",
            "description": "Build a period trial balance with opening, movement, and closing debit-credit columns.",
            "fields": [
                {"name": "organization", "label": "Organization", "col": "col-md-3", "url_name": "organization_select"},
                {"name": "branch", "label": "Branch", "col": "col-md-3", "url_name": "branch_select"},
                {"name": "fiscal_year", "label": "Fiscal Year", "col": "col-md-2", "url_name": "fiscal_year_select"},
                {"name": "date_from", "label": "Date From", "col": "col-md-2", "calendar_switchable": True},
                {"name": "date_to", "label": "Date To", "col": "col-md-2", "calendar_switchable": True},
            ],
        },
        {
            "advanced": True,
            "title": "Display Options",
            "fields": [
                {"name": "show_zero_balances", "label": "Show Zero Balances", "col": "col-md-3", "type": "checkbox"},
            ],
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        },
    ]

    def get_initial_filters(self):
        defaults = self.get_default_reporting_dates()
        return {
            "organization": defaults["organization"],
            "branch": defaults["branch"],
            "fiscal_year": defaults["fiscal_year"],
            "date_from": defaults["default_start"],
            "date_to": defaults["default_end"],
            "show_zero_balances": False,
        }

    def get_form(self):
        return self.form_class(self.get_form_data(), initial=self.get_initial_filters())

    def get_export_columns(self):
        return list(self.export_columns)

    def get_table_rows(self, report_data):
        return list((report_data or {}).get("rows", []))

    def get_report_subtitle(self, report_data=None):
        if report_data:
            pieces = [f"{report_data['date_from']} to {report_data['date_to']}"]
            if report_data.get("fiscal_year"):
                pieces.append(f"Fiscal Year: {report_data['fiscal_year']}")
            if report_data.get("branch"):
                pieces.append(f"Branch: {report_data['branch']}")
            elif report_data.get("organization"):
                pieces.append(f"Organization: {report_data['organization']}")
            return " | ".join(pieces)
        return "Review opening balances, period movement, and closing balances across the full chart."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Opening Debit", "value": summary.get("opening_debit", 0)},
            {"label": "Opening Credit", "value": summary.get("opening_credit", 0)},
            {"label": "Period Debit", "value": summary.get("period_debit", 0)},
            {"label": "Period Credit", "value": summary.get("period_credit", 0)},
            {"label": "Closing Debit", "value": summary.get("closing_debit", 0)},
            {"label": "Closing Credit", "value": summary.get("closing_credit", 0)},
        ]

    def build_report_data(self, cleaned_data):
        report_data = build_trial_balance_report(
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
            show_zero_balances=bool(cleaned_data.get("show_zero_balances")),
        )
        report_data["profit_loss_url"] = self.build_report_link(
            "profit_loss_report",
            generate=1,
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
        )
        report_data["balance_sheet_url"] = self.build_report_link(
            "balance_sheet_report",
            generate=1,
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            as_of_date=cleaned_data.get("date_to"),
        )
        return report_data

    def build_ajax_payload(self, *, form, report_data):
        return self.build_custom_ajax_payload(
            form=form,
            report_data=report_data,
            results_template="account/partials/trial_balance_report_results.html",
        )


class DepreciationEffectReportView(FinancialStatementViewMixin, BaseReportView):
    template_name = "account/depreciation_effect_report.html"
    form_class = DepreciationEffectReportForm
    report_title = "Depreciation Effect Report"
    export_filename = "depreciation_effect_report"
    report_table_id = "depreciationEffectExportTable"
    print_settings = {
        "page_size": "A4",
        "orientation": "landscape",
        "margin": "8mm",
        "summary_columns": 3,
    }
    export_columns = [
        ("asset_class", "Asset Class"),
        ("fixed_asset_account", "Fixed Asset Ledger"),
        ("accumulated_account", "Accumulated Depreciation Ledger"),
        ("expense_account", "Depreciation Expense Ledger"),
        ("opening_cost", "Opening Cost"),
        ("additions", "Additions"),
        ("disposals", "Disposals"),
        ("closing_cost", "Closing Cost"),
        ("opening_accumulated", "Opening Accumulated"),
        ("period_expense", "Depreciation Expense"),
        ("period_accumulated_effect", "Accumulated Depreciation Effect"),
        ("closing_accumulated", "Closing Accumulated"),
        ("opening_nbv", "Opening NBV"),
        ("closing_nbv", "Closing NBV"),
        ("reconciliation_gap", "Reconciliation Gap"),
    ]
    filter_blocks = [
        {
            "title": "Primary Filters",
            "description": "Measure the full accounting effect of depreciation across fixed assets, accumulated depreciation, and expense ledgers.",
            "fields": [
                {"name": "organization", "label": "Organization", "col": "col-md-3", "url_name": "organization_select"},
                {"name": "branch", "label": "Branch", "col": "col-md-3", "url_name": "branch_select"},
                {"name": "fiscal_year", "label": "Fiscal Year", "col": "col-md-2", "url_name": "fiscal_year_select"},
                {"name": "date_from", "label": "Date From", "col": "col-md-2", "calendar_switchable": True},
                {"name": "date_to", "label": "Date To", "col": "col-md-2", "calendar_switchable": True},
            ],
        },
        {
            "advanced": True,
            "title": "Display Options",
            "fields": [
                {"name": "show_zero_balances", "label": "Show Zero Balances", "col": "col-md-3", "type": "checkbox"},
            ],
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        },
    ]

    def get_initial_filters(self):
        defaults = self.get_default_reporting_dates()
        return {
            "organization": defaults["organization"],
            "branch": defaults["branch"],
            "fiscal_year": defaults["fiscal_year"],
            "date_from": defaults["default_start"],
            "date_to": defaults["default_end"],
            "show_zero_balances": False,
        }

    def get_form(self):
        return self.form_class(self.get_form_data(), initial=self.get_initial_filters())

    def get_export_columns(self):
        return list(self.export_columns)

    def get_table_rows(self, report_data):
        return list((report_data or {}).get("rows", []))

    def get_report_subtitle(self, report_data=None):
        if report_data:
            pieces = [f"{report_data['date_from']} to {report_data['date_to']}"]
            if report_data.get("fiscal_year"):
                pieces.append(f"Fiscal Year: {report_data['fiscal_year']}")
            if report_data.get("branch"):
                pieces.append(f"Branch: {report_data['branch']}")
            elif report_data.get("organization"):
                pieces.append(f"Organization: {report_data['organization']}")
            return " | ".join(pieces)
        return "Review P&L depreciation expense, balance-sheet accumulated depreciation, and net book value impact together."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Opening NBV", "value": summary.get("opening_nbv", 0)},
            {"label": "Depreciation Expense", "value": summary.get("period_expense", 0)},
            {"label": "Accumulated Effect", "value": summary.get("period_accumulated_effect", 0)},
            {"label": "Closing NBV", "value": summary.get("closing_nbv", 0)},
            {"label": "Closing Accumulated", "value": summary.get("closing_accumulated", 0)},
            {"label": "Closing Cost", "value": summary.get("closing_cost", 0)},
        ]

    def build_report_data(self, cleaned_data):
        report_data = build_depreciation_effect_report(
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
            show_zero_balances=bool(cleaned_data.get("show_zero_balances")),
        )
        report_data["profit_loss_url"] = self.build_report_link(
            "profit_loss_report",
            generate=1,
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
        )
        report_data["balance_sheet_url"] = self.build_report_link(
            "balance_sheet_report",
            generate=1,
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            as_of_date=cleaned_data.get("date_to"),
        )
        return report_data

    def build_ajax_payload(self, *, form, report_data):
        return self.build_custom_ajax_payload(
            form=form,
            report_data=report_data,
            results_template="account/partials/depreciation_effect_report_results.html",
        )


class GeneralLedgerReportView(FinancialStatementViewMixin, BaseReportView):
    template_name = "account/ledger_book_report.html"
    form_class = GeneralLedgerReportForm
    report_title = "General Ledger"
    export_filename = "general_ledger"
    report_table_id = "generalLedgerExportTable"
    print_settings = {
        "page_size": "A4",
        "orientation": "landscape",
        "margin": "8mm",
        "summary_columns": 3,
    }
    export_columns = [
        ("account", "Account"),
        ("date", "Date"),
        ("entry_no", "Entry No"),
        ("voucher_type", "Voucher Type"),
        ("reference_no", "Reference No"),
        ("description", "Description"),
        ("counterpart", "Counterpart"),
        ("debit", "Debit"),
        ("credit", "Credit"),
        ("running_balance", "Running Balance"),
    ]
    filter_blocks = [
        {
            "title": "Primary Filters",
            "description": "Track opening balance, transactions, and closing balance for a single ledger.",
            "fields": [
                {"name": "organization", "label": "Organization", "col": "col-md-2", "url_name": "organization_select"},
                {"name": "branch", "label": "Branch", "col": "col-md-2", "url_name": "branch_select"},
                {"name": "fiscal_year", "label": "Fiscal Year", "col": "col-md-2", "url_name": "fiscal_year_select"},
                {"name": "account", "label": "Ledger Account", "col": "col-md-3", "url_name": "ledger_account_select"},
                {"name": "date_from", "label": "Date From", "col": "col-md-1", "calendar_switchable": True},
                {"name": "date_to", "label": "Date To", "col": "col-md-2", "calendar_switchable": True},
            ],
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        },
    ]

    def get_initial_filters(self):
        defaults = self.get_default_reporting_dates()
        return {
            "organization": defaults["organization"],
            "branch": defaults["branch"],
            "fiscal_year": defaults["fiscal_year"],
            "date_from": defaults["default_start"],
            "date_to": defaults["default_end"],
        }

    def get_form(self):
        return self.form_class(self.get_form_data(), initial=self.get_initial_filters())

    def get_export_columns(self):
        return list(self.export_columns)

    def get_table_rows(self, report_data):
        return list((report_data or {}).get("rows", []))

    def get_report_subtitle(self, report_data=None):
        if report_data:
            account_label = report_data["account_sections"][0]["account_label"] if report_data.get("account_sections") else ""
            return f"{account_label} | {report_data['date_from']} to {report_data['date_to']}"
        return "Review running transactions for one ledger account."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Opening", "value": summary.get("opening_balance", 0)},
            {"label": "Debit", "value": summary.get("total_debit", 0)},
            {"label": "Credit", "value": summary.get("total_credit", 0)},
            {"label": "Closing", "value": summary.get("closing_balance", 0)},
            {"label": "Transactions", "value": summary.get("transactions", 0)},
        ]

    def build_report_data(self, cleaned_data):
        return build_general_ledger_report(
            account=cleaned_data["account"],
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
        )

    def build_ajax_payload(self, *, form, report_data):
        return self.build_custom_ajax_payload(
            form=form,
            report_data=report_data,
            results_template="account/partials/ledger_book_report_results.html",
        )


class _SpecialBookReportView(FinancialStatementViewMixin, BaseReportView):
    template_name = "account/ledger_book_report.html"
    form_class = SpecialBookReportForm
    report_table_id = "specialBookExportTable"
    export_columns = [
        ("account", "Account"),
        ("date", "Date"),
        ("entry_no", "Entry No"),
        ("voucher_type", "Voucher Type"),
        ("reference_no", "Reference No"),
        ("description", "Description"),
        ("counterpart", "Counterpart"),
        ("debit", "Debit"),
        ("credit", "Credit"),
        ("running_balance", "Running Balance"),
    ]
    print_settings = {
        "page_size": "A4",
        "orientation": "landscape",
        "margin": "8mm",
        "summary_columns": 3,
    }
    book_type = ""
    report_title = "Book Report"
    export_filename = "book_report"
    filter_blocks = [
        {
            "title": "Primary Filters",
            "description": "Review book transactions across one or more matching ledgers.",
            "fields": [
                {"name": "organization", "label": "Organization", "col": "col-md-2", "url_name": "organization_select"},
                {"name": "branch", "label": "Branch", "col": "col-md-2", "url_name": "branch_select"},
                {"name": "fiscal_year", "label": "Fiscal Year", "col": "col-md-2", "url_name": "fiscal_year_select"},
                {"name": "account", "label": "Ledger Filter", "col": "col-md-3", "url_name": "ledger_account_select"},
                {"name": "date_from", "label": "Date From", "col": "col-md-1", "calendar_switchable": True},
                {"name": "date_to", "label": "Date To", "col": "col-md-2", "calendar_switchable": True},
            ],
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        },
    ]

    def get_initial_filters(self):
        defaults = self.get_default_reporting_dates()
        return {
            "organization": defaults["organization"],
            "branch": defaults["branch"],
            "fiscal_year": defaults["fiscal_year"],
            "date_from": defaults["default_start"],
            "date_to": defaults["default_end"],
        }

    def get_form(self):
        return self.form_class(self.get_form_data(), initial=self.get_initial_filters(), book_type=self.book_type)

    def get_export_columns(self):
        return list(self.export_columns)

    def get_table_rows(self, report_data):
        return list((report_data or {}).get("rows", []))

    def get_report_subtitle(self, report_data=None):
        if report_data:
            return f"{report_data['date_from']} to {report_data['date_to']}"
        return "Review opening, movement, and closing balance across matching ledgers."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Ledgers", "value": summary.get("accounts", 0)},
            {"label": "Opening", "value": summary.get("opening_balance", 0)},
            {"label": "Debit", "value": summary.get("total_debit", 0)},
            {"label": "Credit", "value": summary.get("total_credit", 0)},
            {"label": "Closing", "value": summary.get("closing_balance", 0)},
            {"label": "Transactions", "value": summary.get("transactions", 0)},
        ]

    def build_report_data(self, cleaned_data):
        return build_special_book_report(
            book_type=self.book_type,
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            account=cleaned_data.get("account"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
        )

    def build_ajax_payload(self, *, form, report_data):
        return self.build_custom_ajax_payload(
            form=form,
            report_data=report_data,
            results_template="account/partials/ledger_book_report_results.html",
        )


class CashBookReportView(_SpecialBookReportView):
    book_type = "cash"
    report_title = "Cash Book"
    export_filename = "cash_book"
    report_table_id = "cashBookExportTable"


class BankBookReportView(_SpecialBookReportView):
    book_type = "bank"
    report_title = "Bank Book"
    export_filename = "bank_book"
    report_table_id = "bankBookExportTable"


class DayBookReportView(FinancialStatementViewMixin, BaseReportView):
    template_name = "account/day_book_report.html"
    form_class = DayBookReportForm
    report_title = "Day Book"
    export_filename = "day_book"
    report_table_id = "dayBookExportTable"
    export_columns = [
        ("date", "Date"),
        ("entry_no", "Entry No"),
        ("voucher_type", "Voucher Type"),
        ("reference_no", "Reference No"),
        ("narration", "Narration"),
        ("line_summary", "Line Summary"),
        ("total_debit", "Total Debit"),
        ("total_credit", "Total Credit"),
    ]
    print_settings = {
        "page_size": "A4",
        "orientation": "landscape",
        "margin": "8mm",
        "summary_columns": 3,
    }
    filter_blocks = [
        {
            "title": "Primary Filters",
            "description": "Review posted journal entries and line breakdowns for the selected period.",
            "fields": [
                {"name": "organization", "label": "Organization", "col": "col-md-2", "url_name": "organization_select"},
                {"name": "branch", "label": "Branch", "col": "col-md-2", "url_name": "branch_select"},
                {"name": "fiscal_year", "label": "Fiscal Year", "col": "col-md-2", "url_name": "fiscal_year_select"},
                {"name": "voucher_type", "label": "Voucher Type", "col": "col-md-2", "url_name": "voucher_type_select"},
                {"name": "date_from", "label": "Date From", "col": "col-md-2", "calendar_switchable": True},
                {"name": "date_to", "label": "Date To", "col": "col-md-2", "calendar_switchable": True},
            ],
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        },
    ]

    def get_initial_filters(self):
        defaults = self.get_default_reporting_dates()
        return {
            "organization": defaults["organization"],
            "branch": defaults["branch"],
            "fiscal_year": defaults["fiscal_year"],
            "date_from": defaults["default_start"],
            "date_to": defaults["default_end"],
        }

    def get_form(self):
        return self.form_class(self.get_form_data(), initial=self.get_initial_filters())

    def get_export_columns(self):
        return list(self.export_columns)

    def get_table_rows(self, report_data):
        return list((report_data or {}).get("rows", []))

    def get_report_subtitle(self, report_data=None):
        if report_data:
            return f"{report_data['date_from']} to {report_data['date_to']}"
        return "Review posted daybook entries and their line-level accounting impact."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Entries", "value": summary.get("entries", 0)},
            {"label": "Lines", "value": summary.get("lines", 0)},
            {"label": "Debit", "value": summary.get("total_debit", 0)},
            {"label": "Credit", "value": summary.get("total_credit", 0)},
        ]

    def build_report_data(self, cleaned_data):
        return build_day_book_report(
            organization=cleaned_data.get("organization"),
            branch=cleaned_data.get("branch"),
            fiscal_year=cleaned_data.get("fiscal_year"),
            voucher_type=cleaned_data.get("voucher_type"),
            date_from=cleaned_data.get("date_from"),
            date_to=cleaned_data.get("date_to"),
        )

    def build_ajax_payload(self, *, form, report_data):
        return self.build_custom_ajax_payload(
            form=form,
            report_data=report_data,
            results_template="account/partials/day_book_report_results.html",
        )
