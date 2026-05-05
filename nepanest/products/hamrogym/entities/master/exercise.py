from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.exercise_data_table import ExerciseDataTableView, EXERCISE_COLUMNS
from ...forms.exercise_form import ExerciseForm
from ...models import Exercise


register_entity(
    EntityConfig(
        name="exercise",
        url_path="exercise",
        verbose_name="Exercise",
        model=Exercise,
        form_class=ExerciseForm,
        datatable_view=ExerciseDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "muscle_group", "label": "Muscle Group", "type": "select", "required": True, "col": 6, "url_name": "muscle_group_select"},
            {"name": "equipment_type", "label": "Equipment Type", "type": "select", "required": True, "col": 6, "url_name": "equipment_type_select"},
            {"name": "exercise_type", "label": "Exercise Type", "type": "static_select", "required": True, "col": 6, "options": Exercise.EXERCISE_TYPE_CHOICES},
            {"name": "difficulty_level", "label": "Difficulty Level", "type": "static_select", "required": True, "col": 6, "options": Exercise.DIFFICULTY_LEVEL_CHOICES},
            {"name": "instructions", "label": "Instructions", "type": "textarea", "required": False, "col": 12},
            {"name": "precautions", "label": "Precautions", "type": "textarea", "required": False, "col": 12},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in EXERCISE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
