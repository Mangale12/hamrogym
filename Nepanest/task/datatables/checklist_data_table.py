from core.datatables.views import BaseDataTableView
from ..models import Checklist


CHECKLIST_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("project", "project_id.name"),
    ("module", "module_id.name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class ChecklistDataTableView(BaseDataTableView):
    model = Checklist
    columns = CHECKLIST_COLUMNS
    searchable_columns = [
        "name",
        "project_id__name",
        "module_id__name",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "project_id__name",
        "module_id__name",
        "is_active",
        "remarks",
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("project_id", "module_id")
