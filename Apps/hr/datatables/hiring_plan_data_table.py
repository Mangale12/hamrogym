from core.datatables.views import BaseDataTableView
from ..models import HiringPlan


HIRING_PLAN_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class HiringPlanDataTableView(BaseDataTableView):
    model = HiringPlan
    columns = HIRING_PLAN_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
