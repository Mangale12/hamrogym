from core.datatables.views import BaseDataTableView
from ..models import AssetLocation


ASSET_LOCATION_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("branch", "branch.name"),
    ("address", "address"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class AssetLocationDataTableView(BaseDataTableView):
    model = AssetLocation
    columns = ASSET_LOCATION_COLUMNS
    searchable_columns = [
        "name",
        "branch__name",
        "address",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "branch__name",
        "address",
        "is_active",
        "remarks",
    ]
