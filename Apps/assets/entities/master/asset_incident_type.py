from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.asset_incident_type_data_table import AssetIncidentTypeDataTableView, ASSET_INCIDENT_TYPE_COLUMNS
from ...forms.asset_incident_type_form import AssetIncidentTypeForm
from ...models import AssetIncidentType


register_entity(
    EntityConfig(
        name="asset_incident_type",
        url_path="asset-incident-types",
        verbose_name="Asset Incident Types",
        model=AssetIncidentType,
        form_class=AssetIncidentTypeForm,
        datatable_view=AssetIncidentTypeDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "require_approval", "label": "Require Approval", "type": "boolean", "required": False, "col": 6},
            {"name": "auto_create_maintenance", "label": "Auto Create Maintenance", "type": "boolean", "required": False, "col": 6},
            {"name": "financial_impact", "label": "Financial Impact", "type": "boolean", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "boolean", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_INCIDENT_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
