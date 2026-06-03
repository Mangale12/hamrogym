from core.datatables.views import BaseDataTableView
from ..models import ServiceType


SERVICE_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("remarks", "remarks"),
    ("is_active", "is_active"),
]


class ServiceTypeDataTableView(BaseDataTableView):
    model = ServiceType
    columns = SERVICE_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "remarks"
    ]
    orderable_columns = [
        "name",
        "code",
        "remarks",
        "is_active"
    ]
