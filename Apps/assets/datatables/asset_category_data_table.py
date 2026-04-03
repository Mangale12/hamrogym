from core.datatables.views import BaseDataTableView
from ..models import AssetCategory


ASSET_CATEGORY_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("parent", "parent"),
    ("depreciation_applicable", "depreciation_applicable"),
    ("remarks", "remarks"),
]


class AssetCategoryDataTableView(BaseDataTableView):
    model = AssetCategory
    columns = ASSET_CATEGORY_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
        "name",
        "parent",
        "remarks",
    ]
    orderable_columns = [
        # TODO: add orderable fields
        "name",
        "parent",
        "remarks",
    ]
