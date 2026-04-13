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
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4},
            {"name": "code", "label": "Code", "type": "text", "required": False, "col": 4},
            {
                "name": "badge_color",
                "label": "Badge Color",
                "type": "static_select",
                "required": False,
                "col": 4,
                "options": TaskStatus._meta.get_field("badge_color").choices,
            },
            {"name": "sequence", "label": "Sequence", "type": "number", "required": False, "col": 4},
            {"name": "is_default", "label": "Is Default", "type": "checkbox", "required": False, "col": 4},
            {"name": "is_closed", "label": "Is Closed", "type": "checkbox", "required": False, "col": 4},
            {"name": "is_cancelled", "label": "Is Cancelled", "type": "checkbox", "required": False, "col": 4},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in TASK_STATUS_COLUMNS
            if key != "id"
        ],
        reset_defaults={"sequence": 0},
    )
)
