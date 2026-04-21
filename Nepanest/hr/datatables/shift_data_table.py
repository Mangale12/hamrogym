from core.datatables.views import BaseDataTableView
from ..models import Shift


SHIFT_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("start_time", "start_time"),
    ("end_time", "end_time"),
    ("break_start_time", "break_start_time"),
    ("break_end_time", "break_end_time"),
    ("grace_start_time", "grace_start_time"),
    ("grace_end_time", "grace_end_time"),
    ("is_active", "is_active"),
    ("break_duration", "break_duration"),
]


class ShiftDataTableView(BaseDataTableView):
    model = Shift
    columns = SHIFT_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "start_time",
        "end_time",
        "break_start_time",
        "break_end_time",
        "grace_start_time",
        "grace_end_time",
        "is_active",
        "break_duration",
    ]
    orderable_columns = [
        'name',
        'code',
        'start_time',
        'end_time',
        'break_start_time',
        'break_end_time',
        'grace_start_time',
        'grace_end_time',
        'is_active',
        'break_duration',
    ]
