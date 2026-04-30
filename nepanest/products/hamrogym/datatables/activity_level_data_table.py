from core.datatables.views import BaseDataTableView
from ..models import ActivityLevel


ACTIVITY_LEVEL_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class ActivityLevelDataTableView(BaseDataTableView):
    model = ActivityLevel
    columns = ACTIVITY_LEVEL_COLUMNS
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
