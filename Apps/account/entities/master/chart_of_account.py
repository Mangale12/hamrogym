from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.chart_of_account_data_table import ChartOfAccountDataTableView
from ...forms.chart_of_account_form import ChartOfAccountForm
from ...models import ACCOUNT_TYPE_CHOICES, ChartOfAccount


def _account_select_label(obj: ChartOfAccount) -> str:
    return f"{obj.code or 'AUTO'} - {obj.full_path}"


def _prepare_chart_of_account(request, obj: ChartOfAccount):
    obj.is_ledger = False
    obj.allow_direct_posting = False


register_entity(
    EntityConfig(
        name="chart_of_account",
        url_path="chart-of-accounts",
        verbose_name="Chart of Account",
        model=ChartOfAccount,
        form_class=ChartOfAccountForm,
        datatable_view=ChartOfAccountDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "col": 4, "url_name": "branch_select"},
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "col": 4, "url_name": "fiscal_year_select"},
            {
                "name": "parent",
                "label": "Parent Account",
                "type": "select",
                "col": 6,
                "url_name": "chart_of_account_parent_select",
                "attributes": {"data-tree-select": "true"},
            },
            {
                "name": "account_type",
                "label": "Account Type",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": ACCOUNT_TYPE_CHOICES,
            },
            {"name": "name", "label": "Head Name", "type": "text", "required": True, "col": 6},
            {
                "name": "code",
                "label": "Head Code",
                "type": "text",
                "required": False,
                "col": 3,
                "attributes": {"readonly": "readonly"},
            },
           
            {
                "name": "sort_order",
                "label": "Sort Order",
                "type": "number",
                "required": False,
                "col": 3,
                "attributes": {"min": "0"},
            },
            {"name": "is_depreciation", "label": "Is Depreciation Head", "type": "checkbox", "col": 3},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "col": 3},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "col": 12},
        ],
        datatable_columns=[
            {"name": "code", "title": "Head Code"},
            {"name": "tree_name", "title": "Chart Tree"},
            {"name": "account_type", "title": "Account Type"},
            {"name": "report_type", "title": "Report Type"},
            {"name": "parent", "title": "Parent Head"},
            {"name": "is_depreciation", "title": "Depreciation"},
            {"name": "is_active", "title": "Active"},
        ],
        reset_defaults={
            "is_active": True,
            "sort_order": 0,
        },
        select_search_fields=["code", "name", "parent__code", "parent__name"],
        select_label_func=_account_select_label,
        select_order_by="code",
        datatable_options={"order": [[1, "asc"]]},
        pre_save=_prepare_chart_of_account,
    )
)
