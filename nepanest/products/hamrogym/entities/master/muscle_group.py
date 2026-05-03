from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.muscle_group_data_table import MuscleGroupDataTableView, MUSCLE_GROUP_COLUMNS
from ...forms.muscle_group_form import MuscleGroupForm
from ...models import MuscleGroup


register_entity(
    EntityConfig(
        name="muscle_group",
        url_path="muscle-groups",
        verbose_name="Muscle Group",
        model=MuscleGroup,
        form_class=MuscleGroupForm,
        datatable_view=MuscleGroupDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "boolean", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in MUSCLE_GROUP_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
