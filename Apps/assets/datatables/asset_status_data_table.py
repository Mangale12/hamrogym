from core.datatables.views import BaseDataTableView
from ..models import AssetStatus


ASSET_STATUS_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class AssetStatusDataTableView(BaseDataTableView):
    model = AssetStatus
    columns = ASSET_STATUS_COLUMNS
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
