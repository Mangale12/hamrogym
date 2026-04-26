from core.datatables.views import BaseDataTableView
from ..models import GymFacility


GYM_FACILITY_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("branch", "branch.name"),
    ("remarks", "remarks"),
    ("is_active", "is_active"),
]


class GymFacilityDataTableView(BaseDataTableView):
    model = GymFacility
    columns = GYM_FACILITY_COLUMNS
    searchable_columns = ["name", "branch__name", "remarks"]
    orderable_columns = ["name", "branch__name", "remarks", "is_active"]
