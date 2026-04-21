from core.datatables.views import BaseDataTableView

from ..models import Rounding


ROUNDING_COLUMNS = [
    ("code", "code"),
    ("name", "name"),
    ("application_scope", lambda obj: obj.get_application_scope_display()),
    ("rounding_method", lambda obj: obj.get_rounding_method_display()),
    ("round_on", lambda obj: obj.get_round_on_display()),
    ("precision", "precision"),
    ("increment", "increment"),
    ("is_cash_rounding", "is_cash_rounding"),
    ("is_default", "is_default"),
    ("is_active", "is_active"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else None),
    ("fiscal_year", lambda obj: obj.fiscal_year.name if obj.fiscal_year_id else None),
    ("id", "id"),
]


class RoundingDataTableView(BaseDataTableView):
    model = Rounding
    columns = ROUNDING_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "application_scope",
        "rounding_method",
        "round_on",
        "remarks",
        "branch__name",
        "fiscal_year__name",
    ]
    orderable_columns = [
        "code",
        "name",
        "application_scope",
        "rounding_method",
        "round_on",
        "precision",
        "increment",
        "is_cash_rounding",
        "is_default",
        "is_active",
        "branch__name",
        "fiscal_year__name",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("branch", "fiscal_year")

