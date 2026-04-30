from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.membership_plan_data_table import MEMBERSHIP_PLAN_COLUMNS, MembershipPlanDataTableView
from ...forms.membership_plan_form import MembershipPlanForm
from ...models import MembershipPlan


register_entity(
    EntityConfig(
        name="membership_plan",
        url_path="membership-plans",
        verbose_name="Membership Plan",
        model=MembershipPlan,
        form_class=MembershipPlanForm,
        datatable_view=MembershipPlanDataTableView,
        fields=[
            {
                "name": "name",
                "label": "Plan Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Monthly Unlimited",
            },
            {
                "name": "access_type",
                "label": "Access Type",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "access_type_select",
            },
            {
                "name": "duration_days",
                "label": "Duration Days",
                "type": "number",
                "required": True,
                "col": 4,
                "min": 1,
                "step": 1,
            },
            {
                "name": "session_limit",
                "label": "Session Limit",
                "type": "number",
                "required": False,
                "col": 4,
                "min": 0,
                "step": 1,
                "placeholder": "Leave blank for unlimited",
            },
            {
                "name": "freeze_limit_days",
                "label": "Freeze Limit Days",
                "type": "number",
                "required": True,
                "col": 4,
                "min": 0,
                "step": 1,
            },
            {
                "name": "branch",
                "label": "Branch",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "branch_select",
            },
            {
                "name": "is_active",
                "label": "Is Active",
                "type": "checkbox",
                "required": False,
                "col": 6,
            },
            {
                "name": "description",
                "label": "Description",
                "type": "textarea",
                "required": False,
                "col": 12,
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
                "title": "Active" if key == "is_active" else key.replace("_", " ").title(),
                **({"render": "function(data){return data ? 'Yes' : 'No';}"} if key == "is_active" else {}),
            }
            for key, _accessor in MEMBERSHIP_PLAN_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True, "freeze_limit_days": 0},
        select_search_fields=["name", "access_type__name", "access_type__code", "description", "branch__name"],
        select_label_func=lambda obj: f"{obj.name} - {obj.access_type.name}",
    )
)
