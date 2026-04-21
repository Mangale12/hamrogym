from core.datatables.views import BaseDataTableView
from ..models import HiringPlan


HIRING_PLAN_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("fiscal_year", "fiscal_year.name"),
    ("description", "description"),
    ("status", "status"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class HiringPlanDataTableView(BaseDataTableView):
    model = HiringPlan
    columns = HIRING_PLAN_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "fiscal_year__name",
        "description",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "code",
        "fiscal_year__name",
        "description",
        "status",
        "is_active",
        "remarks",
    ]
