from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.fitness_goal_data_table import FITNESS_GOAL_COLUMNS, FitnessGoalDataTableView
from ...forms.fitness_goal_form import FitnessGoalForm
from ...models import FitnessGoal


register_entity(
    EntityConfig(
        name="fitness_goal",
        url_path="fitness-goals",
        verbose_name="Fitness Goal",
        model=FitnessGoal,
        form_class=FitnessGoalForm,
        datatable_view=FitnessGoalDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in FITNESS_GOAL_COLUMNS
            if key != "id"
        ],
        select_search_fields=["name", "code", "remarks"],
        action_state_field="is_system",
        hide_delete_on_values=["true"],
        reset_defaults={"is_active": True},
    )
)
