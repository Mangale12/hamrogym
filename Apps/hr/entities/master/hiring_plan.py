from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.hiring_plan_data_table import HiringPlanDataTableView, HIRING_PLAN_COLUMNS
from ...forms.hiring_plan_form import HiringPlanForm
from ...models import HiringPlan


register_entity(
    EntityConfig(
        name="hiring_plan",
        url_path="hiring-plans",
        verbose_name="Hiring Plan",
        model=HiringPlan,
        form_class=HiringPlanForm,
        datatable_view=HiringPlanDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in HIRING_PLAN_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
