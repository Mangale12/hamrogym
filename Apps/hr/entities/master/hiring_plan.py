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
            {
                "name": "name",
                "label": "Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Annual Hiring Plan",
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "HP-001",
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": HiringPlan._meta.get_field("status").choices,
            },
            {
                "name": "description",
                "label": "Description",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
            {
                "name": "is_active",
                "label": "Active",
                "type": "checkbox",
                "required": False,
                "col": 6,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        datatable_columns=[
            {
                "name": key,
                "title": key.replace("_", " ").title(),
                "render": "function(data){return data ? 'Yes' : 'No';}"
                if key == "is_active"
                else None,
            }
            for key, _accessor in HIRING_PLAN_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True, "status": "draft"},
    )
)
