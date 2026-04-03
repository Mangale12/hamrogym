from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.asset_category_data_table import AssetCategoryDataTableView, ASSET_CATEGORY_COLUMNS
from ...forms.asset_category_form import AssetCategoryForm
from ...models import AssetCategory


register_entity(
    EntityConfig(
        name="asset_category",
        url_path="asset-categories",
        verbose_name="Asset Category",
        model=AssetCategory,
        form_class=AssetCategoryForm,
        datatable_view=AssetCategoryDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "boolean", "col": 6},
            {"name": "parent", "label": "Parent Category", "type": "select", "col": 6, "url_path": "asset_category_select"},
            {"name": "depreciation_applicable", "label": "Depreciation Applicable", "type": "boolean", "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_CATEGORY_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
