from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.service_data_table import ServiceDataTableView, SERVICE_COLUMNS
from ...forms.service_form import ServiceForm
from ...models import Service


register_entity(
    EntityConfig(
        name="service",
        url_path="services",
        verbose_name="Service",
        model=Service,
        form_class=ServiceForm,
        datatable_view=ServiceDataTableView,
        template_name="crm/entity_index.html",
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "service_type", "label": "Service Type", "type": "select", "required": False, "col": 6, "url_name": "service_type_select"},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name" : "default_price", "label": "Default Price", "type": "number", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
            
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in SERVICE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
