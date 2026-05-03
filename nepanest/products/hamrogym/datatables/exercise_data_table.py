from core.datatables.views import BaseDataTableView
from ..models import Exercise


EXERCISE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("muscle_group", "muscle_group.name"),
    ("equipment_type", "equipment_type.name"),
    ("exercise_type", "exercise_type"),
    ("difficulty_level", "difficulty_level"),
    ("instructions", "instructions"),
    ("precautions", "precautions"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class ExerciseDataTableView(BaseDataTableView):
    model = Exercise
    columns = EXERCISE_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
        "name",
        "muscle_group__name",
        "equipment_type__name",
        "exercise_type",
        "difficulty_level",
        "instructions",
        "precautions",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        # TODO: add orderable fields
        "name",
        "muscle_group__name",
        "equipment_type__name",
        "exercise_type",
        "difficulty_level",
        "instructions",
        "precautions",
        "is_active",
        "remarks",
    ]
