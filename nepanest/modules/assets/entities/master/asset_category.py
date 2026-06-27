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
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "col": 6},
            {"name": "parent", "label": "Parent Category", "type": "select", "col": 6, "url_name": "asset_category_select"},
            {"name": "depreciation_applicable", "label": "Depreciation Applicable", "type": "checkbox", "col": 6},
            {
                "name": "depreciation_method",
                "label": "Depreciation Method",
                "type": "static_select",
                "col": 6,
                "options": AssetCategory.DEPRECIATION_METHOD_CHOICES,
            },
            {"name": "default_useful_life_months", "label": "Default Useful Life Months", "type": "number", "col": 6},
            {
                "name": "fixed_asset_account",
                "label": "Fixed Asset Ledger",
                "type": "select",
                "col": 4,
                "url_name": "ledger_account_select",
            },
            {
                "name": "depreciation_expense_account",
                "label": "Depreciation Expense Ledger",
                "type": "select",
                "col": 4,
                "url_name": "ledger_account_select",
            },
            {
                "name": "accumulated_depreciation_account",
                "label": "Accumulated Depreciation Ledger",
                "type": "select",
                "col": 4,
                "url_name": "ledger_account_select",
            },
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
