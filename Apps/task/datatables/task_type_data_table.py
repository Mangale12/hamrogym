from core.datatables.views import BaseDataTableView
from ..models import TaskType


TASK_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("sequence", "sequence"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class TaskTypeDataTableView(BaseDataTableView):
    model = TaskType
    columns = TASK_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "code",
        "sequence",
        "is_active",
        "remarks",
    ]
