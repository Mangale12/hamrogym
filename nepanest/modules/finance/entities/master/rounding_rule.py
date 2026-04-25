from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.rounding_rule_data_table import RoundingRuleDataTableView
from ...forms import RoundingRuleForm
from ...models import RoundingRule


register_entity(
    EntityConfig(
        name="rounding_rule",
        url_path="rounding-rules",
        verbose_name="Rounding Rule",
        model=RoundingRule,
        form_class=RoundingRuleForm,
        datatable_view=RoundingRuleDataTableView,
        fields=[
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": False, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "priority", "label": "Priority", "type": "number", "required": True, "col": 4, "attributes": {"min": "1"}},
            {"name": "name", "label": "Rule Name", "type": "text", "required": True, "col": 4, "placeholder": "Cash sales under 1000"},
            {"name": "rounding", "label": "Rounding", "type": "select", "required": True, "col": 4, "url_name": "rounding_select"},
            {"name": "application_scope", "label": "Scope", "type": "static_select", "required": True, "col": 4, "options": RoundingRule._meta.get_field("application_scope").choices},
            {"name": "document_type", "label": "Document Type", "type": "static_select", "required": True, "col": 4, "options": RoundingRule._meta.get_field("document_type").choices},
            {"name": "party_type", "label": "Party Type", "type": "select", "required": False, "col": 4, "url_name": "party_type_select"},
            {"name": "currency", "label": "Currency", "type": "select", "required": False, "col": 4, "url_name": "currency_select"},
            {"name": "payment_method", "label": "Payment Method", "type": "select", "required": False, "col": 4, "url_name": "payment_method_select"},
            {"name": "min_amount", "label": "Min Amount", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "max_amount", "label": "Max Amount", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "stop_processing", "label": "Stop Processing", "type": "checkbox", "required": False, "col": 3},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 3, "default": True},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Optional condition notes or policy remarks."},
        ],
        datatable_columns=[
            {"name": "name", "title": "Rule Name"},
            {"name": "rounding", "title": "Rounding"},
            {"name": "application_scope", "title": "Scope"},
            {"name": "document_type", "title": "Document Type"},
            {"name": "party_type", "title": "Party Type", "render": "function(data){return data || '-';}"},
            {"name": "currency", "title": "Currency", "render": "function(data){return data || '-';}"},
            {"name": "payment_method", "title": "Payment Method", "render": "function(data){return data || '-';}"},
            {"name": "min_amount", "title": "Min Amount", "render": "function(data){return data || '-';}"},
            {"name": "max_amount", "title": "Max Amount", "render": "function(data){return data || '-';}"},
            {"name": "priority", "title": "Priority"},
            {"name": "stop_processing", "title": "Stop", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "branch", "title": "Branch", "render": "function(data){return data || '-';}"},
            {"name": "fiscal_year", "title": "Fiscal Year", "render": "function(data){return data || '-';}"},
        ],
        reset_defaults={
            "priority": 1,
            "application_scope": "both",
            "document_type": "all",
            "is_active": True,
        },
        select_search_fields=["name", "rounding__code", "rounding__name", "document_type", "application_scope"],
        select_label_func=lambda obj: f"{obj.name} ({obj.rounding.code})",
    )
)

