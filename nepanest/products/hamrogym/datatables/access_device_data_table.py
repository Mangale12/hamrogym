from core.datatables.views import BaseDataTableView

from ..models import AccessDevice


ACCESS_DEVICE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("device_type", "device_type"),
    ("location", "location"),
    ("status", "status"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
    ("is_active", "is_active"),
]


class AccessDeviceDataTableView(BaseDataTableView):
    model = AccessDevice
    columns = ACCESS_DEVICE_COLUMNS
    searchable_columns = ["name", "device_type", "location", "status", "branch__name", "remarks"]
    orderable_columns = ["name", "device_type", "location", "status", "branch__name", "is_active"]
