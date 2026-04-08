from core.datatables.views import BaseDataTableView
from ..models import TaskStatus


TASK_STATUS_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class TaskStatusDataTableView(BaseDataTableView):
    model = TaskStatus
    columns = TASK_STATUS_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
