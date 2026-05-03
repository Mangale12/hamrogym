from core.datatables.views import BaseDataTableView
from ..models import MuscleGroup


MUSCLE_GROUP_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class MuscleGroupDataTableView(BaseDataTableView):
    model = MuscleGroup
    columns = MUSCLE_GROUP_COLUMNS
    searchable_columns = [
        "name",
        "is_active",
        "remarks"
    ]
    orderable_columns = [
        "name",
        "is_active",
        "remarks"
    ]
