from core.config import EntityConfig
from core.registry import register_entity

from ..datatables.client_data_table import CLIENT_COLUMNS, ClientDataTableView
from ..forms.client_form import ClientForm
from ..models import Client


register_entity(
    EntityConfig(
        name="client",
        url_path="clients",
        verbose_name="Client",
        model=Client,
        form_class=ClientForm,
        datatable_view=ClientDataTableView,
        fields=[
            {"name": "business_name", "label": "Business Name", "type": "text", "required": True, "col": 6},
            {"name": "client_code", "label": "Client Code", "type": "text", "required": True, "col": 6},
            {"name": "contact_email", "label": "Contact Email", "type": "email", "required": True, "col": 6},
            {"name": "contact_phone", "label": "Contact Phone", "type": "text", "required": False, "col": 6},
            {"name": "address", "label": "Address", "type": "textarea", "required": False, "col": 12},
            {
                "name": "plan",
                "label": "Plan",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": Client.Plan.choices,
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": Client.Status.choices,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in CLIENT_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "plan": Client.Plan.STARTER,
            "status": Client.Status.TRIAL,
        },
    )
)
