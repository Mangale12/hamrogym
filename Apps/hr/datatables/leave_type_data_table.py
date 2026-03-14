from core.datatables.views import BaseDataTableView
from ..models import leave_type


LEAVE_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class leave_typeDataTableView(BaseDataTableView):
    model = leave_type
    columns = LEAVE_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "is_active",
       
    ]
