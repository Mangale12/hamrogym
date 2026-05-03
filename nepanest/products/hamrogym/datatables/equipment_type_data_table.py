from core.datatables.views import BaseDataTableView
from ..models import EquipmentType


EQUIPMENT_TYPE_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class EquipmentTypeDataTableView(BaseDataTableView):
    model = EquipmentType
    columns = EQUIPMENT_TYPE_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
        "name",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        # TODO: add orderable fields
        "name",
        "is_active",
        "remarks",
    ]
