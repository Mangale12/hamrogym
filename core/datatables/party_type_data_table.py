from core.datatables.views import BaseDataTableView

from ..models import PartyType


PARTY_TYPE_COLUMNS = [
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
    ("id", "id"),
]


class PartyTypeDataTableView(BaseDataTableView):
    model = PartyType
    columns = PARTY_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "is_active",
        "remarks",
        "id",
    ]
