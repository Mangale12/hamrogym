from core.datatables.views import BaseDataTableView
from nepanest.modules.leave.models import LeaveType


LEAVE_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_paid", "is_paid"),
    ("is_carry_forward", "is_carry_forward"),
    ("is_encashable", "is_encashable"),
    ("requires_attachment", "requires_attachment"),
    ("requires_approval", "requires_approval"),
    ("max_days_per_year", "max_days_per_year"),
    ("color", "color"),
    ("description", "description"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class LeaveTypeDataTableView(BaseDataTableView):
    model = LeaveType
    columns = LEAVE_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "remarks",
        "description",
    ]
    orderable_columns = [
        "id",
        "name",
        "is_active",
        "description",
    ]
