from core.datatables.views import BaseDataTableView
from ..models import TaskLabel


TASK_LABEL_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("color", "color"),
    ("sequence", "sequence"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
    # TODO: add columns
]


class TaskLabelDataTableView(BaseDataTableView):
    model = TaskLabel
    columns = TASK_LABEL_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "color",
        "sequence",
        "is_active",
        "remarks",
        "created_at",
        "updated_at",
    ]
    orderable_columns = [
        "name",
        "code",
        "color",
        "sequence",
        "is_active",
        "remarks",
        "created_at",
        "updated_at",
    ]
