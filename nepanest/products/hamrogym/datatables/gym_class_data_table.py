from core.datatables.views import BaseDataTableView
from ..models import GymClass


GYM_CLASS_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("class_type.name", "class_type"),
    ("difficulty_level", "difficulty_level"),
    ("max_capacity", "max_capacity"),
    ("duration_minutes", "duration_minutes"),
    ("trainer.name", "trainer"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
    # TODO: add columns
]


class GymClassDataTableView(BaseDataTableView):
    model = GymClass
    columns = GYM_CLASS_COLUMNS
    searchable_columns = [
        "name",
        "class_type__name",
        "difficulty_level",
        "max_capacity",
        "duration_minutes",
        "trainer__name",
        "is_active",
        "remarks",
        # TODO: add searchable fields
    ]
    orderable_columns = [
        "name",
        "class_type__name",
        "difficulty_level",
        "max_capacity",
        "duration_minutes",
        "trainer__name",
        "is_active",
        "remarks",
        # TODO: add orderable fields
    ]
