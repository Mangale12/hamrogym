from core.datatables.views import BaseDataTableView

from ..models import Tax


def amount_value_display(obj):
    if obj.calculation_method == "fixed":
        return str(obj.fixed_amount)
    return f"{obj.rate}%"


TAX_COLUMNS = [
    ("code", "code"),
    ("name", "name"),
    ("tax_type", lambda obj: obj.get_tax_type_display()),
    ("calculation_method", lambda obj: obj.get_calculation_method_display()),
    ("application_scope", lambda obj: obj.get_application_scope_display()),
    ("amount_value", amount_value_display),
    ("rate", "rate"),
    ("fixed_amount", "fixed_amount"),
    ("effective_from", lambda obj: obj.effective_from.isoformat() if obj.effective_from else None),
    ("effective_to", lambda obj: obj.effective_to.isoformat() if obj.effective_to else None),
    ("is_inclusive", "is_inclusive"),
    ("is_recoverable", "is_recoverable"),
    ("is_active", "is_active"),
    ("id", "id"),
]


class TaxDataTableView(BaseDataTableView):
    model = Tax
    columns = TAX_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "tax_type",
        "calculation_method",
        "application_scope",
        "remarks",
    ]
    orderable_columns = [
        "code",
        "name",
        "tax_type",
        "calculation_method",
        "application_scope",
        "rate",
        "rate",
        "fixed_amount",
        "effective_from",
        "effective_to",
        "is_inclusive",
        "is_recoverable",
        "is_active",
        "id",
    ]
