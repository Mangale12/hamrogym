from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.credit_limit_data_table import CreditLimitDataTableView
from ...forms import CreditLimitForm
from ...models import CreditLimit


register_entity(
    EntityConfig(
        name="credit_limit",
        url_path="credit-limits",
        verbose_name="Credit Limit",
        model=CreditLimit,
        form_class=CreditLimitForm,
        datatable_view=CreditLimitDataTableView,
        fields=[
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": False, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "party", "label": "Party", "type": "select", "required": True, "col": 4, "url_name": "party_select"},
            {"name": "policy", "label": "Policy", "type": "select", "required": False, "col": 4, "url_name": "credit_policy_select"},
            {"name": "credit_limit", "label": "Credit Limit", "type": "number", "required": True, "col": 4, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "used_credit", "label": "Used Credit", "type": "number", "required": False, "col": 4, "attributes": {"disabled": "disabled"}},
            {"name": "available_credit", "label": "Available Credit", "type": "number", "required": False, "col": 4, "attributes": {"disabled": "disabled"}},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 4, "default": True},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "party", "title": "Party"},
            {"name": "policy", "title": "Policy", "render": "function(data){return data || '-';}"},
            {"name": "credit_limit", "title": "Credit Limit"},
            {"name": "used_credit", "title": "Used Credit"},
            {"name": "available_credit", "title": "Available"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "branch", "title": "Branch", "render": "function(data){return data || '-';}"},
            {"name": "fiscal_year", "title": "Fiscal Year", "render": "function(data){return data || '-';}"},
        ],
        reset_defaults={
            "credit_limit": "0.00",
            "is_active": True,
        },
        select_search_fields=["party__name", "party__display_name"],
        select_label_func=lambda obj: f"{obj.party} - {obj.credit_limit}",
    )
)

