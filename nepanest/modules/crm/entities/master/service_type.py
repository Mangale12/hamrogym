from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.service_type_data_table import ServiceTypeDataTableView, SERVICE_TYPE_COLUMNS
from ...forms.service_type_form import ServiceTypeForm
from ...models import ServiceType


register_entity(
    EntityConfig(
        name="service_type",
        url_path="service-types",
        verbose_name="Service Type",
        model=ServiceType,
        form_class=ServiceTypeForm,
        datatable_view=ServiceTypeDataTableView,
        template_name="crm/entity_index.html",
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in SERVICE_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
