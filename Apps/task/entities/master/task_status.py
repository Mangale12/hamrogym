from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.task_status_data_table import TaskStatusDataTableView, TASK_STATUS_COLUMNS
from ...forms.task_status_form import TaskStatusForm
from ...models import TaskStatus


register_entity(
    EntityConfig(
        name="task_status",
        url_path="task-status",
        verbose_name="Task Status",
        model=TaskStatus,
        form_class=TaskStatusForm,
        datatable_view=TaskStatusDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in TASK_STATUS_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
