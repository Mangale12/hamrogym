from core.datatables.views import BaseDataTableView

from ..models import CreditLimit


CREDIT_LIMIT_COLUMNS = [
    ("party", lambda obj: str(obj.party)),
    ("policy", lambda obj: obj.policy.name if obj.policy_id else None),
    ("credit_limit", "credit_limit"),
    ("used_credit", "used_credit"),
    ("available_credit", lambda obj: obj.available_credit),
    ("is_active", "is_active"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else None),
    ("fiscal_year", lambda obj: obj.fiscal_year.name if obj.fiscal_year_id else None),
    ("id", "id"),
]


class CreditLimitDataTableView(BaseDataTableView):
    model = CreditLimit
    columns = CREDIT_LIMIT_COLUMNS
    searchable_columns = [
        "party__name",
        "party__display_name",
        "policy__name",
        "remarks",
        "branch__name",
        "fiscal_year__name",
    ]
    orderable_columns = [
        "party__name",
        "policy__name",
        "credit_limit",
        "used_credit",
        "is_active",
        "branch__name",
        "fiscal_year__name",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("party", "policy", "branch", "fiscal_year")

