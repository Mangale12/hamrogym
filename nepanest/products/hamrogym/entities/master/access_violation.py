from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.access_violation_data_table import ACCESS_VIOLATION_COLUMNS, AccessViolationDataTableView
from ...forms.access_violation_form import AccessViolationForm
from ...models import AccessViolation


register_entity(
    EntityConfig(
        name="access_violation",
        url_path="access-violations",
        verbose_name="Access Violation",
        model=AccessViolation,
        form_class=AccessViolationForm,
        datatable_view=AccessViolationDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 6, "url_name": "member_select"},
            {"name": "membership", "label": "Membership", "type": "select", "required": False, "col": 6, "url_name": "member_membership_select"},
            {
                "name": "violation_type",
                "label": "Violation Type",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": [("", "Select Violation Type"), *AccessViolation.ViolationType.choices],
            },
            {"name": "detected_at", "label": "Detected At", "type": "datetime-local", "required": True, "col": 4},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "action_taken", "label": "Action Taken", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ACCESS_VIOLATION_COLUMNS
            if key != "id"
        ],
        select_search_fields=["member__member_code", "member__party__name", "violation_type"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.get_violation_type_display()}",
    )
)
