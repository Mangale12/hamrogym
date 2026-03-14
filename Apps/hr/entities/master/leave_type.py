from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.leave_type_data_table import (
    LEAVE_TYPE_COLUMNS,
    leave_typeDataTableView,
)
from ...forms.leave_type_form import leave_typeForm
from ...models import leave_type


register_entity(
    EntityConfig(
        name="leave_type",
        url_path="leave-types",
        verbose_name="Leave Type",
        model=leave_type,
        form_class=leave_typeForm,
        datatable_view=leave_typeDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "boolean", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
            
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LEAVE_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
