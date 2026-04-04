from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.asset_location_data_table import AssetLocationDataTableView, ASSET_LOCATION_COLUMNS
from ...forms.asset_location_form import AssetLocationForm
from ...models import AssetLocation


register_entity(
    EntityConfig(
        name="asset_location",
        url_path="asset-locations",
        verbose_name="Asset Location",
        model=AssetLocation,
        form_class=AssetLocationForm,
        datatable_view=AssetLocationDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "branch", "label": "Branch", "type": "select", "required": True, "col": 6, "url_name": "branch_select"},
            {"name": "address", "label": "Address", "type": "text", "required": False, "col": 12},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_LOCATION_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
