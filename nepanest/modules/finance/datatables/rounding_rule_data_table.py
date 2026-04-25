from core.datatables.views import BaseDataTableView

from ..models import RoundingRule


ROUNDING_RULE_COLUMNS = [
    ("name", "name"),
    ("rounding", lambda obj: str(obj.rounding)),
    ("application_scope", lambda obj: obj.get_application_scope_display()),
    ("document_type", lambda obj: obj.get_document_type_display()),
    ("party_type", lambda obj: obj.party_type.name if obj.party_type_id else None),
    ("currency", lambda obj: obj.currency.code if obj.currency_id else None),
    ("payment_method", lambda obj: obj.payment_method.name if obj.payment_method_id else None),
    ("min_amount", "min_amount"),
    ("max_amount", "max_amount"),
    ("priority", "priority"),
    ("stop_processing", "stop_processing"),
    ("is_active", "is_active"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else None),
    ("fiscal_year", lambda obj: obj.fiscal_year.name if obj.fiscal_year_id else None),
    ("id", "id"),
]


class RoundingRuleDataTableView(BaseDataTableView):
    model = RoundingRule
    columns = ROUNDING_RULE_COLUMNS
    searchable_columns = [
        "name",
        "rounding__code",
        "rounding__name",
        "application_scope",
        "document_type",
        "party_type__name",
        "currency__code",
        "currency__name",
        "payment_method__code",
        "payment_method__name",
        "remarks",
        "branch__name",
        "fiscal_year__name",
    ]
    orderable_columns = [
        "name",
        "rounding__code",
        "application_scope",
        "document_type",
        "party_type__name",
        "currency__code",
        "payment_method__name",
        "min_amount",
        "max_amount",
        "priority",
        "stop_processing",
        "is_active",
        "branch__name",
        "fiscal_year__name",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related(
            "rounding",
            "party_type",
            "currency",
            "payment_method",
            "branch",
            "fiscal_year",
        )

