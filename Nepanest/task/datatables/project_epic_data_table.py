from core.datatables.views import BaseDataTableView

from ..models import ProjectEpic


PROJECT_EPIC_COLUMNS = [
    ("id", "id"),
    ("project", "project.name"),
    ("name", "name"),
    ("status", "status"),
    ("priority", "priority"),
    ("progress", "progress"),
    ("start_date", "start_date"),
    ("end_date", "end_date"),
    ("is_active", "is_active"),
]


class ProjectEpicDataTableView(BaseDataTableView):
    model = ProjectEpic
    columns = PROJECT_EPIC_COLUMNS
    searchable_columns = [
        "project__name",
        "name",
        "description",
        "status",
        "priority",
        "remarks",
    ]
    orderable_columns = [
        "project__name",
        "name",
        "status",
        "priority",
        "progress",
        "start_date",
        "end_date",
        "is_active",
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("project")
