from core.datatables.views import BaseDataTableView

from ..models import CreditPolicy


CREDIT_POLICY_COLUMNS = [
    ("name", "name"),
    ("allow_over_limit", "allow_over_limit"),
    ("over_limit_percentage", "over_limit_percentage"),
    ("block_sales", "block_sales"),
    ("is_default", "is_default"),
    ("is_active", "is_active"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else None),
    ("fiscal_year", lambda obj: obj.fiscal_year.name if obj.fiscal_year_id else None),
    ("id", "id"),
]


class CreditPolicyDataTableView(BaseDataTableView):
    model = CreditPolicy
    columns = CREDIT_POLICY_COLUMNS
    searchable_columns = [
        "name",
        "remarks",
        "branch__name",
        "fiscal_year__name",
    ]
    orderable_columns = [
        "name",
        "allow_over_limit",
        "over_limit_percentage",
        "block_sales",
        "is_default",
        "is_active",
        "branch__name",
        "fiscal_year__name",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("branch", "fiscal_year")

