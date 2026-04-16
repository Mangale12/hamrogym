from core.datatables.views import BaseDataTableView

from ..models import ChartOfAccount


def _tree_name(obj):
    depth = max((obj.report_level or 1) - 1, 0)
    return f"{'&nbsp;&nbsp;&nbsp;&nbsp;' * depth}{obj.name}"


CHART_OF_ACCOUNT_COLUMNS = [
    ("id", "id"),
    ("code", "code"),
    ("tree_name", _tree_name),
    ("account_type", lambda obj: obj.get_account_type_display()),
    ("report_type", lambda obj: obj.get_report_type_display()),
    ("parent", lambda obj: obj.parent.code if obj.parent_id else ""),
    ("report_level", "report_level"),
    ("allow_direct_posting", "allow_direct_posting"),
    ("is_depreciation", "is_depreciation"),
    ("is_active", "is_active"),
]


class ChartOfAccountDataTableView(BaseDataTableView):
    model = ChartOfAccount
    columns = CHART_OF_ACCOUNT_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "account_type",
        "report_type",
        "parent__code",
        "parent__name",
        "remarks",
    ]
    orderable_columns = [
        "code",
        "name",
        "account_type",
        "report_type",
        "parent__code",
        "report_level",
        "allow_direct_posting",
        "is_depreciation",
        "is_active",
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_ledger=False)
            .select_related("parent", "organization", "branch", "fiscal_year")
            .order_by("code", "sort_order", "id")
        )

