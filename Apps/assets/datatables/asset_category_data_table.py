from core.datatables.views import BaseDataTableView
from ..models import AssetCategory


ASSET_CATEGORY_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("parent", "parent"),
    ("depreciation_applicable", "depreciation_applicable"),
    ("depreciation_method", "depreciation_method"),
    ("default_useful_life_months", "default_useful_life_months"),
    ("remarks", "remarks"),
]


class AssetCategoryDataTableView(BaseDataTableView):
    model = AssetCategory
    columns = ASSET_CATEGORY_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
        "name",
        "parent",
        "depreciation_method",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "parent",
        "depreciation_method",
        "default_useful_life_months",
        "remarks",
    ]
