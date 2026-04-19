from core.datatables.views import BaseDataTableView

from ..models import Party


PARTY_COLUMNS = [
    ("name", "name"),
    ("display_name", lambda obj: obj.display_name or obj.name),
    ("party_type", "party_type.name"),
    ("category", lambda obj: obj.get_category_display()),
    ("pan_number", "pan_number"),
    ("vat_number", "vat_number"),
    ("is_active", "is_active"),
    ("id", "id"),
]


class PartyDataTableView(BaseDataTableView):
    model = Party
    columns = PARTY_COLUMNS
    searchable_columns = [
        "name",
        "display_name",
        "party_type__name",
        "category",
        "pan_number",
        "vat_number",
        "registration_number",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "display_name",
        "party_type__name",
        "category",
        "pan_number",
        "vat_number",
        "is_active",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("party_type")
