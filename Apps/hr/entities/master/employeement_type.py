from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.employeement_type_data_table import (
    EMPLOYEEMENT_TYPE_COLUMNS,
    employeement_typeDataTableView,
)
from ...forms.employeement_type_form import employeement_typeForm
from ...models import employeement_type


register_entity(
    EntityConfig(
        name="employeement_type",
        url_path="employeement-types",
        verbose_name="Employeement Type",
        model=employeement_type,
        form_class=employeement_typeForm,
        datatable_view=employeement_typeDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in EMPLOYEEMENT_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
