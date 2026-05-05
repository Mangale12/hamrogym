from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.diet_plan_data_table import DietPlanDataTableView, DIET_PLAN_COLUMNS
from ...forms.diet_plan_form import DietPlanForm
from ...models import DietPlan


register_entity(
    EntityConfig(
        name="diet_plan",
        url_path="diet-plans",
        verbose_name="Diet Plan",
        model=DietPlan,
        form_class=DietPlanForm,
        datatable_view=DietPlanDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "fitness_goal", "label": "Fitness Goal", "type": "select", "required": True, "col": 6},
            {"name": "duration_days", "label": "Duration (Days)", "type": "number", "required": True, "col": 6},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "trainer", "label": "Trainer", "type": "select", "required": False, "col": 6},
            {"name": "status", "label": "Status", "type": "checkbox", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12}
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in DIET_PLAN_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
