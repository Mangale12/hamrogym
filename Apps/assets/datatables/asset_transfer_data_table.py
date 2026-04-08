from core.datatables.views import BaseDataTableView

from ..models import AssetTransfer


ASSET_TRANSFER_COLUMNS = [
    ("id", "id"),
    ("asset", "asset.name"),
    ("transfer_date", "transfer_date"),
    ("from_location", "from_location.name"),
    ("to_location", "to_location.name"),
    ("from_department", "from_department.name"),
    ("to_department", "to_department.name"),
    (
        "transferred_by",
        lambda obj: obj.transferred_by.get_full_name() or obj.transferred_by.username
        if obj.transferred_by
        else "",
    ),
    (
        "received_by",
        lambda obj: obj.received_by.get_full_name() or obj.received_by.username
        if obj.received_by
        else "",
    ),
    ("remarks", "remarks"),
]


class AssetTransferDataTableView(BaseDataTableView):
    model = AssetTransfer
    columns = ASSET_TRANSFER_COLUMNS
    searchable_columns = [
        "asset__name",
        "asset__code",
        "from_location__name",
        "to_location__name",
        "from_department__name",
        "to_department__name",
        "transferred_by__first_name",
        "transferred_by__last_name",
        "transferred_by__username",
        "received_by__first_name",
        "received_by__last_name",
        "received_by__username",
        "remarks",
    ]
    orderable_columns = [
        "asset__name",
        "transfer_date",
        "from_location__name",
        "to_location__name",
        "from_department__name",
        "to_department__name",
        "transferred_by__username",
        "received_by__username",
        "remarks",
    ]
