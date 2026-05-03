from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.access_rule_data_table import ACCESS_RULE_COLUMNS, AccessRuleDataTableView
from ...forms.access_rule_form import AccessRuleForm
from ...models import AccessRule


register_entity(
    EntityConfig(
        name="access_rule",
        url_path="access-rules",
        verbose_name="Access Rule",
        model=AccessRule,
        form_class=AccessRuleForm,
        datatable_view=AccessRuleDataTableView,
        fields=[
            {
                "name": "membership_plan",
                "label": "Membership Plan",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "membership_plan_select",
            },
            {
                "name": "rule_type",
                "label": "Rule Type",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": [("", "Select Rule Type"), *AccessRule.RuleType.choices],
            },
            {"name": "time_range_start", "label": "Time Start", "type": "time", "required": False, "col": 3},
            {"name": "time_range_end", "label": "Time End", "type": "time", "required": False, "col": 3},
            {"name": "max_checkins_per_day", "label": "Max Check-ins Per Day", "type": "number", "required": False, "col": 3, "min": 0, "step": 1},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 3, "url_name": "branch_select"},
            {"name": "allowed_days", "label": "Allowed Days", "type": "text", "required": False, "col": 12, "placeholder": "Mon,Tue,Wed"},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {
                "name": key,
                "title": "Active" if key == "is_active" else key.replace("_", " ").title(),
                **({"render": "function(data){return data ? 'Yes' : 'No';}"} if key == "is_active" else {}),
            }
            for key, _accessor in ACCESS_RULE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
        select_search_fields=["membership_plan__name", "rule_type", "allowed_days"],
        select_label_func=lambda obj: f"{obj.membership_plan.name} - {obj.get_rule_type_display()}",
    )
)
