from core.datatables.views import BaseDataTableView
from ..models import DietPlan


DIET_PLAN_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("fitness_goal.name", "fitness_goal"),
    ("duration_days", "duration_days"),
    ("description", "description"),
    ("trainer.name", "trainer"),
    ("status", "status"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
    # TODO: add columns
]


class DietPlanDataTableView(BaseDataTableView):
    model = DietPlan
    columns = DIET_PLAN_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
        "name",
        "fitness_goal__name",
        "trainer__name",
        "status",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        # TODO: add orderable fields
        "name",
        "fitness_goal__name",
        "duration_days",
        "trainer__name",
        "status",
        "is_active",
        "remarks",
    ]
