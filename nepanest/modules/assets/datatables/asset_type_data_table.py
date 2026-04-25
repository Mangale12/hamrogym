from core.datatables.views import BaseDataTableView
from ..models import AssetType


ASSET_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("category", "category.name"),
    ("depreciation_applicable", "depreciation_applicable"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class AssetTypeDataTableView(BaseDataTableView):
    model = AssetType
    columns = ASSET_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "category__name",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "category__name",
        "depreciation_applicable",
        "is_active",
        "remarks",
    ]
