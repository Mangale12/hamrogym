from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.tax_group_item_data_table import TaxGroupItemDataTableView
from ...forms import TaxGroupItemForm
from ...models import TaxGroupItem


register_entity(
    EntityConfig(
        name="tax_group_item",
        url_path="tax-group-items",
        verbose_name="Tax Group Item",
        model=TaxGroupItem,
        form_class=TaxGroupItemForm,
        datatable_view=TaxGroupItemDataTableView,
        fields=[
            {"name": "tax_group", "label": "Tax Group", "type": "select", "required": True, "col": 6, "url_name": "tax_group_select"},
            {"name": "tax", "label": "Tax", "type": "select", "required": True, "col": 6, "url_name": "tax_select"},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": True, "col": 3, "attributes": {"min": "1"}},
            {"name": "override_rate", "label": "Override Rate %", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "is_compound", "label": "Compound", "type": "checkbox", "required": False, "col": 3},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 3, "default": True},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "tax_group", "title": "Tax Group"},
            {"name": "tax", "title": "Tax"},
            {"name": "sequence", "title": "Sequence"},
            {"name": "override_rate", "title": "Override Rate %"},
            {"name": "is_compound", "title": "Compound", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
        ],
        reset_defaults={"sequence": 1, "is_active": True},
        select_search_fields=["tax_group__code", "tax_group__name", "tax__code", "tax__name"],
        select_label_func=lambda obj: f"{obj.tax_group} - {obj.tax}",
    )
)

