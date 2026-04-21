from core.datatables.views import BaseDataTableView
from ..models import TaskModule


TASK_MODULE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
    # TODO: add columns
]


class TaskModuleDataTableView(BaseDataTableView):
    model = TaskModule
    columns = TASK_MODULE_COLUMNS
    searchable_columns = [
        "name",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "is_active",
        "remarks",
    ]
