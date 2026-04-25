from core.datatables.views import BaseDataTableView
from ..models import TaskStatus


TASK_STATUS_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("badge_color", "badge_color"),
    ("sequence", "sequence"),
    ("is_default", "is_default"),
    ("is_closed", "is_closed"),
    ("is_cancelled", "is_cancelled"),
]


class TaskStatusDataTableView(BaseDataTableView):
    model = TaskStatus
    columns = TASK_STATUS_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "badge_color",
    ]
    orderable_columns = [
        "name",
        "code",
        "badge_color",
        "sequence",
        "is_default",
        "is_closed",
        "is_cancelled",
    ]
