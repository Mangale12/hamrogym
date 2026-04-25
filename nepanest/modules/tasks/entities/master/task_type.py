from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.task_type_data_table import TaskTypeDataTableView, TASK_TYPE_COLUMNS
from ...forms.task_type_form import TaskTypeForm
from ...models import TaskType


register_entity(
    EntityConfig(
        name="task_type",
        url_path="task-types",
        verbose_name="Task Type",
        model=TaskType,
        form_class=TaskTypeForm,
        datatable_view=TaskTypeDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4},
            {"name": "code", "label": "Code", "type": "text", "required": False, "col": 4},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": False, "col": 4},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in TASK_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"sequence": 0, "is_active": True},
    )
)
