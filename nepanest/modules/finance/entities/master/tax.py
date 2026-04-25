from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.tax_data_table import TaxDataTableView
from ...forms import TaxForm
from ...models import Tax


register_entity(
    EntityConfig(
        name="tax",
        url_path="taxes",
        verbose_name="Tax",
        model=Tax,
        form_class=TaxForm,
        datatable_view=TaxDataTableView,
        fields=[
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 4, "placeholder": "VAT13"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4, "placeholder": "VAT 13%"},
            {"name": "tax_type", "label": "Tax Type", "type": "static_select", "required": True, "col": 4, "options": Tax._meta.get_field("tax_type").choices},
            {"name": "calculation_method", "label": "Calculation Method", "type": "static_select", "required": True, "col": 4, "options": Tax._meta.get_field("calculation_method").choices},
            {"name": "application_scope", "label": "Application Scope", "type": "static_select", "required": True, "col": 4, "options": Tax._meta.get_field("application_scope").choices},
            {"name": "rate", "label": "Rate %", "type": "number", "required": False, "col": 2, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "fixed_amount", "label": "Fixed Amount", "type": "number", "required": False, "col": 2, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "effective_from", "label": "Effective From", "type": "date", "required": False, "col": 3},
            {"name": "effective_to", "label": "Effective To", "type": "date", "required": False, "col": 3},
            {"name": "is_inclusive", "label": "Inclusive", "type": "checkbox", "required": False, "col": 3},
            {"name": "is_recoverable", "label": "Recoverable", "type": "checkbox", "required": False, "col": 3, "default": True},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 3, "default": True},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "code", "title": "Code"},
            {"name": "name", "title": "Name"},
            {"name": "tax_type", "title": "Tax Type"},
            {"name": "calculation_method", "title": "Calculation"},
            {"name": "application_scope", "title": "Scope"},
            {"name": "amount_value", "title": "Amount"},
            {"name": "rate", "title": "Rate %"},
            {"name": "fixed_amount", "title": "Fixed Amount"},
            {"name": "effective_from", "title": "Effective From", "render": "function(data){return data || '-';}"},
            {"name": "effective_to", "title": "Effective To", "render": "function(data){return data || '-';}"},
            {"name": "is_inclusive", "title": "Inclusive", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_recoverable", "title": "Recoverable", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
        ],
        reset_defaults={
            "tax_type": "vat",
            "calculation_method": "percentage",
            "application_scope": "both",
            "is_recoverable": True,
            "is_active": True,
        },
        select_search_fields=["code", "name", "tax_type"],
        select_label_func=lambda obj: f"{obj.code} - {obj.name}",
    )
)
