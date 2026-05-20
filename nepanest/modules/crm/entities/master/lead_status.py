from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.lead_status_data_table import LeadStatusDataTableView, LEAD_STATUS_COLUMNS
from ...forms.lead_status_form import LeadStatusForm
from ...models import LeadStatus


register_entity(
    EntityConfig(
        name="lead_status",
        url_path="lead-statuses",
        verbose_name="Lead Status",
        model=LeadStatus,
        form_class=LeadStatusForm,
        datatable_view=LeadStatusDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LEAD_STATUS_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
