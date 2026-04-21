from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.asset_condition_data_table import AssetConditionDataTableView, ASSET_CONDITION_COLUMNS
from ...forms.asset_condition_form import AssetConditionForm
from ...models import AssetCondition


register_entity(
    EntityConfig(
        name="asset_condition",
        url_path="asset-conditions",
        verbose_name="Asset Condition",
        model=AssetCondition,
        form_class=AssetConditionForm,
        datatable_view=AssetConditionDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_CONDITION_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
    )
)
