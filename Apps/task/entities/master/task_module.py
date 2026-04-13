from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.task_module_data_table import TaskModuleDataTableView, TASK_MODULE_COLUMNS
from ...forms.task_module_form import TaskModuleForm
from ...models import TaskModule


register_entity(
    EntityConfig(
        name="task_module",
        url_path="task-modules",
        verbose_name="Task Modules",
        model=TaskModule,
        form_class=TaskModuleForm,
        datatable_view=TaskModuleDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in TASK_MODULE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
