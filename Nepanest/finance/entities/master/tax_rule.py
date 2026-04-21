from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.tax_rule_data_table import TaxRuleDataTableView
from ...forms import TaxRuleForm
from ...models import TaxRule


register_entity(
    EntityConfig(
        name="tax_rule",
        url_path="tax-rules",
        verbose_name="Tax Rule",
        model=TaxRule,
        form_class=TaxRuleForm,
        datatable_view=TaxRuleDataTableView,
        fields=[
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 3, "placeholder": "VAT-SALE"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 5, "placeholder": "Sales VAT Rule"},
            {"name": "tax", "label": "Tax", "type": "select", "required": True, "col": 4, "url_name": "tax_select"},
            {"name": "rule_type", "label": "Rule Type", "type": "static_select", "required": True, "col": 4, "options": TaxRule._meta.get_field("rule_type").choices},
            {"name": "application_scope", "label": "Application Scope", "type": "static_select", "required": True, "col": 4, "options": TaxRule._meta.get_field("application_scope").choices},
            {"name": "party_type", "label": "Party Type", "type": "select", "required": False, "col": 4, "url_name": "party_type_select"},
            {"name": "country", "label": "Country", "type": "select", "required": False, "col": 4, "url_name": "country_select"},
            {"name": "priority", "label": "Priority", "type": "number", "required": True, "col": 2, "attributes": {"min": "1"}},
            {"name": "min_amount", "label": "Min Amount", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "max_amount", "label": "Max Amount", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "stop_processing", "label": "Stop Processing", "type": "checkbox", "required": False, "col": 3},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 3, "default": True},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "code", "title": "Code"},
            {"name": "name", "title": "Name"},
            {"name": "tax", "title": "Tax"},
            {"name": "rule_type", "title": "Rule Type"},
            {"name": "application_scope", "title": "Scope"},
            {"name": "party_type", "title": "Party Type", "render": "function(data){return data || '-';}"},
            {"name": "country", "title": "Country", "render": "function(data){return data || '-';}"},
            {"name": "priority", "title": "Priority"},
            {"name": "stop_processing", "title": "Stop", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
        ],
        reset_defaults={"rule_type": "line_net", "application_scope": "both", "priority": 1, "is_active": True},
        select_search_fields=["code", "name", "tax__code", "tax__name", "party_type__name", "country__name"],
        select_label_func=lambda obj: f"{obj.code} - {obj.name}",
    )
)
