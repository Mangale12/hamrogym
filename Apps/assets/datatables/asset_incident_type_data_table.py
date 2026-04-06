from core.datatables.views import BaseDataTableView
from ..models import AssetIncidentType


ASSET_INCIDENT_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("require_approval", "require_approval"),
    ("auto_create_maintenance", "auto_create_maintenance"),
    ("financial_impact", "financial_impact"),
    ("is_active", "is_active"),
]


class AssetIncidentTypeDataTableView(BaseDataTableView):
    model = AssetIncidentType
    columns = ASSET_INCIDENT_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "code",
    ]
    orderable_columns = [
        "id",
        "name",
        "code",
        "require_approval",
        "auto_create_maintenance",
        "financial_impact",
        "is_active",
    ]
