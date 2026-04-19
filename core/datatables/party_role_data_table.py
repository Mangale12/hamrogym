from core.datatables.views import BaseDataTableView

from ..models import PartyRole


PARTY_ROLE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class PartyRoleDataTableView(BaseDataTableView):
    model = PartyRole
    columns = PARTY_ROLE_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "code",
        "is_active",
        "remarks",
    ]
