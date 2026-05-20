from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.gym_class_data_table import GymClassDataTableView, GYM_CLASS_COLUMNS
from ...forms.gym_class_form import GymClassForm
from ...models.exercise import DIFFICULTY_LEVEL_CHOICES
from ...models import GymClass


register_entity(
    EntityConfig(
        name="gym_class",
        url_path="gym-classes",
        verbose_name="Gym Class",
        model=GymClass,
        form_class=GymClassForm,
        datatable_view=GymClassDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "class_type", "label": "Class Type", "type": "select", "required": False, "col": 6, "url_name": "gym_class_type_select"},
            {"name": "difficulty_level", "label": "Difficulty Level", "type": "static_select", "required": True, "col": 6, "options":DIFFICULTY_LEVEL_CHOICES},
            {"name": "max_capacity", "label": "Max Capacity", "type": "number", "required": True, "col": 6},
            {"name": "duration_minutes", "label": "Duration (Minutes)", "type": "number", "required": True, "col": 6},
            {"name": "trainer", "label": "Trainer", "type": "select", "required": False, "col": 6, "url_name": "trainer_select"},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in GYM_CLASS_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
