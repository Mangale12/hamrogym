from core.datatables.views import BaseDataTableView

from ..models import Discount


DISCOUNT_COLUMNS = [
    ("code", "code"),
    ("name", "name"),
    ("discount_type", lambda obj: obj.get_discount_type_display()),
    ("value", "value"),
    ("scope", lambda obj: obj.get_scope_display()),
    ("fiscal_year", lambda obj: obj.fiscal_year.name if obj.fiscal_year_id else None),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else None),
    ("id", "id"),
]


class DiscountDataTableView(BaseDataTableView):
    model = Discount
    columns = DISCOUNT_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "discount_type",
        "scope",
        "fiscal_year__name",
        "branch__name",
    ]
    orderable_columns = [
        "code",
        "name",
        "discount_type",
        "value",
        "scope",
        "fiscal_year__name",
        "branch__name",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("fiscal_year", "branch")
