from core.datatables.views import BaseDataTableView
from ..models import GymClassType 


GYM_CLASS_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
  
    # TODO: add columns
]


class GymClassTypeDataTableView(BaseDataTableView):
    model = GymClassType
    columns = GYM_CLASS_COLUMNS
    searchable_columns = [
        "name",
        "is_active",
        # TODO: add searchable fields
    ]
    orderable_columns = [
        "id",
        "name",
        "is_active",
    ]
