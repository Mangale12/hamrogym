from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.lead_data_table import LeadDataTableView, LEAD_COLUMNS
from ...forms.lead_form import LeadForm
from ...models import Lead


register_entity(
    EntityConfig(
        name="lead",
        url_path="leads",
        verbose_name="Lead",
        model=Lead,
        form_class=LeadForm,
        datatable_view=LeadDataTableView,
        show_view=False,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "email", "label": "Email", "type": "email", "required": False, "col": 6},
            {"name": "phone", "label": "Phone", "type": "text", "required": False, "col": 6},
            {"name": "company_name", "label": "Company Name", "type": "text", "required": False, "col": 6},
            {"name": "lead_source", "label": "Lead Source", "type": "select", "required": False, "col": 6, "url_name": "lead_source_select"},
            {"name": "lead_status", "label": "Lead Status", "type": "select", "required": False, "col": 6, "url_name": "lead_status_select"},
            {"name": "assigned_to", "label": "Assigned To", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
            {"name": "service", "label": "Service", "type": "select", "required": False, "col": 6, "url_name": "service_select"},
            {"name": "budget", "label": "Budget", "type": "number", "required": False, "col": 6},
            {"name": "last_contacted", "label": "Last Contacted", "type": "datetime-local", "required": False, "col": 6},
            {"name": "next_followup", "label": "Next Follow-up", "type": "datetime-local", "required": False, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LEAD_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
        action_buttons=[
            {
                "label": "Open",
                "title": "Open CRM lead workspace",
                "icon_class": "fas fa-sitemap",
                "class_name": "btn-outline-warning",
                "href_url": "/core/crm/leads/{id}/view/",
            },
        ]
    )
)
