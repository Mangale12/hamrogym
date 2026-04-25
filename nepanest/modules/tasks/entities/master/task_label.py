from core.choices import BADGE_COLOR_CHOICES
from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.task_label_data_table import TaskLabelDataTableView, TASK_LABEL_COLUMNS
from ...forms.task_label_form import TaskLabelForm
from ...models import TaskLabel


register_entity(
    EntityConfig(
        name="task_label",
        url_path="task-labels",
        verbose_name="Task Label",
        model=TaskLabel,
        form_class=TaskLabelForm,
        datatable_view=TaskLabelDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": False, "col": 6},
            {"name": "color", "label": "Color", "type": "static_select", "required": False, "col": 6, "options": BADGE_COLOR_CHOICES},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in TASK_LABEL_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
