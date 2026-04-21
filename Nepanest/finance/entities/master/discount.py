from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.discount_data_table import DiscountDataTableView
from ...forms import DiscountForm
from ...models import Discount


register_entity(
    EntityConfig(
        name="discount",
        url_path="discounts",
        verbose_name="Discount",
        model=Discount,
        form_class=DiscountForm,
        datatable_view=DiscountDataTableView,
        fields=[
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": False, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 4, "placeholder": "DISC10"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4, "placeholder": "Standard 10% Discount"},
            {"name": "discount_type", "label": "Discount Type", "type": "static_select", "required": True, "col": 4, "options": Discount._meta.get_field("discount_type").choices},
            {"name": "value", "label": "Value", "type": "number", "required": True, "col": 4, "attributes": {"step": "0.0001", "min": "0"}},
            {"name": "scope", "label": "Scope", "type": "static_select", "required": True, "col": 4, "options": Discount._meta.get_field("scope").choices},
        ],
        datatable_columns=[
            {"name": "code", "title": "Code"},
            {"name": "name", "title": "Name"},
            {"name": "discount_type", "title": "Discount Type"},
            {"name": "value", "title": "Value"},
            {"name": "scope", "title": "Scope"},
            {"name": "fiscal_year", "title": "Fiscal Year", "render": "function(data){return data || '-';}"},
            {"name": "branch", "title": "Branch", "render": "function(data){return data || '-';}"},
        ],
        reset_defaults={"discount_type": "percentage", "scope": "line"},
        select_search_fields=["code", "name", "discount_type", "scope"],
        select_label_func=lambda obj: f"{obj.code} - {obj.name}",
    )
)
