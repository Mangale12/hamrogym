from core.datatables.views import BaseDataTableView
from ..models import WorkoutPlan


WORKOUT_PLAN_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("fitness_goal", lambda obj: obj.fitness_goal.name if obj.fitness_goal else "-"),
    ("difficulty_level", lambda obj: obj.get_difficulty_level_display() if obj.difficulty_level else "-"),
    ("duration_week", lambda obj: obj.duration_week or "-"),
    ("days_per_week", lambda obj: obj.days_per_week or "-"),
]


class WorkoutPlanDataTableView(BaseDataTableView):
    model = WorkoutPlan
    columns = WORKOUT_PLAN_COLUMNS
    searchable_columns = [
        "name",
        "fitness_goal__name",
        "difficulty_level",
    ]
    orderable_columns = [
        "id",
        "name",
        "fitness_goal__name",
        "difficulty_level",
        "duration_week",
        "days_per_week",
    ]
