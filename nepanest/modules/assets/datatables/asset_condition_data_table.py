from core.datatables.views import BaseDataTableView
from ..models import AssetCondition


ASSET_CONDITION_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class AssetConditionDataTableView(BaseDataTableView):
    model = AssetCondition
    columns = ASSET_CONDITION_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "code",
        "is_active",
        "remarks",
    ]
