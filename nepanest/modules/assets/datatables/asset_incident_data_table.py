from core.datatables.views import BaseDataTableView
from ..models import AssetIncident


ASSET_INCIDENT_COLUMNS = [
    ("id", "id"),
    ("asset", "asset.name"),
    ("employee", lambda obj: obj.employee.get_full_name() or obj.employee.username if obj.employee else ""),
    ("incident_type", "incident_type.name"),
    ("incident_date", "incident_date"),
    (
        "maintenance_record",
        lambda obj: (
            f"{obj.maintenance_record.maintenance_type} ({obj.maintenance_record.get_status_display()})"
            if hasattr(obj, "maintenance_record") and obj.maintenance_record
            else "-"
        ),
    ),
    ("estimated_cost", "estimated_cost"),
    ("final_cost", "final_cost"),
    ("approval_deduction_cost", "approval_deduction_cost"),
    ("reported_by", lambda obj: obj.reported_by.get_full_name() or obj.reported_by.username if obj.reported_by else ""),
    ("approved_by", lambda obj: obj.approved_by.get_full_name() or obj.approved_by.username if obj.approved_by else ""),
    ("branch", "branch.name"),
    ("status", "status"),
    ("remarks", "remarks"),
]


class AssetIncidentDataTableView(BaseDataTableView):
    model = AssetIncident
    columns = ASSET_INCIDENT_COLUMNS
    searchable_columns = [
        "asset__name",
        "asset__code",
        "employee__first_name",
        "employee__last_name",
        "employee__username",
        "incident_type__name",
        "incident_date",
        "maintenance_record__maintenance_type",
        "maintenance_record__status",
        "reported_by__first_name",
        "reported_by__last_name",
        "reported_by__username",
        "approved_by__first_name",
        "approved_by__last_name",
        "approved_by__username",
        "branch__name",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "asset__name",
        "employee__first_name",
        "incident_type__name",
        "incident_date",
        "maintenance_record__maintenance_type",
        "estimated_cost",
        "final_cost",
        "approval_deduction_cost",
        "reported_by__username",
        "approved_by__username",
        "branch__name",
        "status",
        "remarks",
    ]
