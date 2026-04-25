from core.datatables.views import BaseDataTableView

from ..models import TaxRule


TAX_RULE_COLUMNS = [
    ("code", "code"),
    ("name", "name"),
    ("tax", "tax.name"),
    ("rule_type", lambda obj: obj.get_rule_type_display()),
    ("application_scope", lambda obj: obj.get_application_scope_display()),
    ("party_type", lambda obj: obj.party_type.name if obj.party_type_id else None),
    ("country", lambda obj: obj.country.name if obj.country_id else None),
    ("min_amount", "min_amount"),
    ("max_amount", "max_amount"),
    ("priority", "priority"),
    ("stop_processing", "stop_processing"),
    ("is_active", "is_active"),
    ("id", "id"),
]


class TaxRuleDataTableView(BaseDataTableView):
    model = TaxRule
    columns = TAX_RULE_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "tax__code",
        "tax__name",
        "rule_type",
        "application_scope",
        "party_type__name",
        "country__name",
        "remarks",
    ]
    orderable_columns = [
        "code",
        "name",
        "tax__name",
        "rule_type",
        "application_scope",
        "party_type__name",
        "country__name",
        "min_amount",
        "max_amount",
        "priority",
        "stop_processing",
        "is_active",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("tax", "party_type", "country")
