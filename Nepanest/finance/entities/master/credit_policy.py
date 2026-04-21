from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.credit_policy_data_table import CreditPolicyDataTableView
from ...forms import CreditPolicyForm
from ...models import CreditPolicy


register_entity(
    EntityConfig(
        name="credit_policy",
        url_path="credit-policies",
        verbose_name="Credit Policy",
        model=CreditPolicy,
        form_class=CreditPolicyForm,
        datatable_view=CreditPolicyDataTableView,
        fields=[
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": False, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4, "placeholder": "Standard Customer Credit"},
            {"name": "allow_over_limit", "label": "Allow Over Limit", "type": "checkbox", "required": False, "col": 3},
            {"name": "over_limit_percentage", "label": "Over Limit %", "type": "number", "required": True, "col": 3, "attributes": {"step": "0.01", "min": "0", "max": "100"}},
            {"name": "block_sales", "label": "Block Sales", "type": "checkbox", "required": False, "col": 3},
            {"name": "is_default", "label": "Default", "type": "checkbox", "required": False, "col": 3},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 3, "default": True},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "name", "title": "Name"},
            {"name": "allow_over_limit", "title": "Allow Over Limit", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "over_limit_percentage", "title": "Over Limit %"},
            {"name": "block_sales", "title": "Block Sales", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_default", "title": "Default", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "branch", "title": "Branch", "render": "function(data){return data || '-';}"},
            {"name": "fiscal_year", "title": "Fiscal Year", "render": "function(data){return data || '-';}"},
        ],
        reset_defaults={
            "over_limit_percentage": "0.00",
            "block_sales": True,
            "is_active": True,
        },
        select_search_fields=["name"],
        select_label_func=lambda obj: obj.name,
    )
)

