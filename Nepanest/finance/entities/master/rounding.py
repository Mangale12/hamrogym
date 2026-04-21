from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.rounding_data_table import RoundingDataTableView
from ...forms import RoundingForm
from ...models import Rounding


register_entity(
    EntityConfig(
        name="rounding",
        url_path="roundings",
        verbose_name="Rounding",
        model=Rounding,
        form_class=RoundingForm,
        datatable_view=RoundingDataTableView,
        fields=[
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": False, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "application_scope", "label": "Scope", "type": "static_select", "required": True, "col": 4, "options": Rounding._meta.get_field("application_scope").choices},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 3, "placeholder": "ROUND-01"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 5, "placeholder": "Standard Cash Rounding"},
            {"name": "rounding_method", "label": "Method", "type": "static_select", "required": True, "col": 4, "options": Rounding._meta.get_field("rounding_method").choices},
            {"name": "round_on", "label": "Round On", "type": "static_select", "required": True, "col": 4, "options": Rounding._meta.get_field("round_on").choices},
            {"name": "precision", "label": "Precision", "type": "number", "required": True, "col": 2, "attributes": {"min": "0", "max": "6"}},
            {"name": "increment", "label": "Increment", "type": "number", "required": True, "col": 2, "attributes": {"step": "0.000001", "min": "0.000001"}},
            {"name": "is_cash_rounding", "label": "Cash Rounding", "type": "checkbox", "required": False, "col": 2},
            {"name": "is_default", "label": "Default", "type": "checkbox", "required": False, "col": 2},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 2, "default": True},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Usage notes for invoice, bill, or payment rounding."},
        ],
        datatable_columns=[
            {"name": "code", "title": "Code"},
            {"name": "name", "title": "Name"},
            {"name": "application_scope", "title": "Scope"},
            {"name": "rounding_method", "title": "Method"},
            {"name": "round_on", "title": "Round On"},
            {"name": "precision", "title": "Precision"},
            {"name": "increment", "title": "Increment"},
            {"name": "is_cash_rounding", "title": "Cash", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_default", "title": "Default", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "branch", "title": "Branch", "render": "function(data){return data || '-';}"},
            {"name": "fiscal_year", "title": "Fiscal Year", "render": "function(data){return data || '-';}"},
        ],
        reset_defaults={
            "application_scope": "both",
            "rounding_method": "half_up",
            "round_on": "document",
            "precision": 2,
            "increment": "0.010000",
            "is_active": True,
        },
        select_search_fields=["code", "name", "application_scope", "rounding_method", "round_on"],
        select_label_func=lambda obj: f"{obj.code} - {obj.name}",
    )
)

