from core.datatables.views import BaseDataTableView

from ..models import AccessType


ACCESS_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("description", "description"),
    ("branch", "branch.name"),
    ("is_active", "is_active"),
]


class AccessTypeDataTableView(BaseDataTableView):
    model = AccessType
    columns = ACCESS_TYPE_COLUMNS
    searchable_columns = ["name", "code", "description", "branch__name", "remarks"]
    orderable_columns = ["name", "code", "description", "branch__name", "is_active"]
