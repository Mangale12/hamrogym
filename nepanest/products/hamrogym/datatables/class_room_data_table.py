from core.datatables.views import BaseDataTableView
from ..models import ClassRoom


CLASS_ROOM_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("capacity", "capacity"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class ClassRoomDataTableView(BaseDataTableView):
    model = ClassRoom
    columns = CLASS_ROOM_COLUMNS
    searchable_columns = [
        "name",
        "capacity",
        "is_active",
        "remarks"
    ]
    orderable_columns = [
        "name",
        "capacity",
        "is_active",
        "remarks"
    ]
