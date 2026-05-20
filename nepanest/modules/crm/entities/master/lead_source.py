from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.lead_source_data_table import LeadSourceDataTableView, LEAD_SOURCE_COLUMNS
from ...forms.lead_source_form import LeadSourceForm
from ...models import LeadSource


register_entity(
    EntityConfig(
        name="lead_source",
        url_path="lead-sources",
        verbose_name="Lead Source",
        model=LeadSource,
        form_class=LeadSourceForm,
        datatable_view=LeadSourceDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LEAD_SOURCE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
