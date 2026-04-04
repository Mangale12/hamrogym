from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.asset_status_data_table import AssetStatusDataTableView, ASSET_STATUS_COLUMNS
from ...forms.asset_status_form import AssetStatusForm
from ...models import AssetStatus


register_entity(
    EntityConfig(
        name="asset_status",
        url_path="asset-statuses",
        verbose_name="Asset Status",
        model=AssetStatus,
        form_class=AssetStatusForm,
        datatable_view=AssetStatusDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_STATUS_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
    )
)
