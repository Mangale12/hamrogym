from core.datatables.views import BaseDataTableView
from ..models import LeaveType


LEAVE_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class LeaveTypeDataTableView(BaseDataTableView):
    model = LeaveType
    columns = LEAVE_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "is_active",
       
    ]
