from core.config import EntityConfig
from core.registry import register_entity

from ..datatables.subscription_data_table import SUBSCRIPTION_COLUMNS, SubscriptionDataTableView
from ..forms.subscription_form import SubscriptionForm
from ..models import Subscription


register_entity(
    EntityConfig(
        name="subscription",
        url_path="subscriptions",
        verbose_name="Subscription",
        model=Subscription,
        form_class=SubscriptionForm,
        datatable_view=SubscriptionDataTableView,
        fields=[
            {
                "name": "client",
                "label": "Client",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "client_select",
            },
            {"name": "plan_name", "label": "Plan Name", "type": "text", "required": True, "col": 6},
            {"name": "amount", "label": "Amount", "type": "number", "required": True, "col": 6, "step": "0.01"},
            {"name": "interval", "label": "Interval", "type": "text", "required": True, "col": 6},
            {"name": "status", "label": "Status", "type": "text", "required": True, "col": 6},
            {"name": "period_start", "label": "Period Start", "type": "date", "required": True, "col": 6},
            {"name": "period_end", "label": "Period End", "type": "date", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in SUBSCRIPTION_COLUMNS
            if key != "id"
        ],
        select_search_fields=["client__business_name", "client__client_code", "plan_name", "interval", "status"],
        select_label_func=lambda obj: f"{obj.client} - {obj.plan_name} ({obj.period_start} to {obj.period_end})",
    )
)
