from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.asset_type_data_table import AssetTypeDataTableView, ASSET_TYPE_COLUMNS
from ...forms.asset_type_form import AssetTypeForm
from ...models import AssetType


register_entity(
    EntityConfig(
        name="asset_type",
        url_path="asset-types",
        verbose_name="Asset Type",
        model=AssetType,
        form_class=AssetTypeForm,
        datatable_view=AssetTypeDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {
                "name": "category",
                "label": "Category",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "asset_category_select",
            },
            {
                "name": "depreciation_applicable",
                "label": "Depreciation Applicable",
                "type": "checkbox",
                "required": False,
                "col": 12,
            },
            {
                "name": "is_active",
                "label": "Is Active",
                "type": "checkbox",
                "required": False,
                "col": 12,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
