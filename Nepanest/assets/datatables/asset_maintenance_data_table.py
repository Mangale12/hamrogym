from core.datatables.views import BaseDataTableView

from ..models import AssetMaintenanceRecord


ASSET_MAINTENANCE_COLUMNS = [
    ("id", "id"),
    ("asset", "asset.name"),
    (
        "incident",
        lambda obj: f"{obj.incident.incident_type} ({obj.incident.incident_date})"
        if obj.incident
        else "-",
    ),
    ("maintenance_date", "maintenance_date"),
    ("maintenance_type", "maintenance_type"),
    ("vendor", "vendor.name"),
    ("cost", "cost"),
    (
        "performed_by",
        lambda obj: obj.performed_by.get_full_name() or obj.performed_by.username
        if obj.performed_by
        else "",
    ),
    ("status", "status"),
    ("remarks", "remarks"),
]


class AssetMaintenanceRecordDataTableView(BaseDataTableView):
    model = AssetMaintenanceRecord
    columns = ASSET_MAINTENANCE_COLUMNS
    searchable_columns = [
        "asset__name",
        "asset__code",
        "incident__incident_type__name",
        "maintenance_type",
        "vendor__name",
        "performed_by__first_name",
        "performed_by__last_name",
        "performed_by__username",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "asset__name",
        "incident__incident_type__name",
        "maintenance_date",
        "maintenance_type",
        "vendor__name",
        "cost",
        "performed_by__username",
        "status",
        "remarks",
    ]
