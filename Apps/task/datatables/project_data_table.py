from core.datatables.views import BaseDataTableView
from ..models import Project


PROJECT_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("module", "module.name"),
    ("manager", "manager.username"),
    ("status", "status"),
    ("priority", "priority"),
    ("start_date", "start_date"),
    ("end_date", "end_date"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class ProjectDataTableView(BaseDataTableView):
    model = Project
    columns = PROJECT_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "module__name",
        "manager__username",
        "description",
        "status",
        "priority",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "code",
        "module__name",
        "manager__username",
        "status",
        "priority",
        "start_date",
        "end_date",
        "is_active",
        "remarks",
    ]
