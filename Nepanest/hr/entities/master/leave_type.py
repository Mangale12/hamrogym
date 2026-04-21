from Nepanest.hr.models.leave_type import LeavePolicy
from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.leave_type_data_table import (
    LEAVE_TYPE_COLUMNS,
    LeaveTypeDataTableView,
)
from ...forms.leave_type_form import LeaveTypeForm
from ...models import LeaveType
from core.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

LEAVE_TYPE_POLICY = {
    "title" : "Leave Policy",
    "layout" : "table",
    "allow_add" : True,
    "fields": [
        {"name": "employment_type", "label": "Employment Type", "type": "select", "required": True, "url_name": "employeement_type_select"},
        {"name": "days_allowed", "label": "Days Allowed", "type": "number", "required": True},
        {"name": "accrual_type", "label": "Accrual Type", "type": "static_select", "required": True, "options": [("monthly", "Monthly"), ("yearly", "Yearly")]},
        {"name": "accrual_rate", "label": "Accrual Rate", "type": "number", "required": True},
        {"name": "carry_forward_limit", "label": "Carry Forward Limit", "type": "number", "required": True},
        {"name": "carry_forward_expiry_days", "label": "Carry Forward Expiry Days", "type": "number", "required": True},
        {"name": "max_consecutive_days", "label": "Max Consecutive Days", "type": "number", "required": True},
        {"name": "min_service_days", "label": "Min Service Days", "type": "number", "required": True},
        {"name": "allow_half_day", "label": "Allow Half Day", "type": "checkbox", "required": True},
        {"name": "allow_negative_balance", "label": "Allow Negative Balance", "type": "checkbox", "required": True},
        {"name": "effective_from", "label": "Effective From", "type": "date", "required": True},
        {"name": "effective_to", "label": "Effective To", "type": "date", "required": False},
        {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False},
    ]
}

LEAVE_TYPE_POLICY_RELATION = RelatedDynamicSectionConfig(
    section_name="leave_type_policy",
    related_model=LeavePolicy,
    parent_field="leave_type",
    fields=[
        "employment_type",
        "days_allowed",
        "accrual_type",
        "accrual_rate",
        "carry_forward_limit",
        "carry_forward_expiry_days",
        "max_consecutive_days",
        "min_service_days",
        "allow_half_day",
        "allow_negative_balance",
        "effective_from",
        "effective_to",
        "is_active",
        "remarks",
    ],
    required_fields=[
        "employment_type",
        "days_allowed",
        "accrual_type",
        "accrual_rate",
        "carry_forward_limit",
        "carry_forward_expiry_days",
        "min_service_days",
        "effective_from",
    ],
    bool_fields=[
        "allow_half_day",
        "allow_negative_balance",
        "is_active",
    ],
    empty_check_fields=[
        "employment_type",
        "days_allowed",
        "accrual_type",
        "accrual_rate",
        "carry_forward_limit",
        "carry_forward_expiry_days",
        "max_consecutive_days",
        "min_service_days",
        "effective_from",
        "effective_to",
        "remarks",
    ],
    order_by="effective_from",
)

_save_leave_policy_changes = build_related_section_saver(LEAVE_TYPE_POLICY_RELATION)
__load_leave_policy_changes = build_related_section_loader(LEAVE_TYPE_POLICY_RELATION)

register_entity(
    EntityConfig(
        name="leave_type",
        url_path="leave-types",
        verbose_name="Leave Type",
        model=LeaveType,
        form_class=LeaveTypeForm,
        datatable_view=LeaveTypeDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_paid", "label": "Is Paid", "type": "checkbox", "required": True, "col": 6},
            {"name": "is_carry_forward", "label": "Is Carry Forward", "type": "checkbox", "required": True, "col": 6},
            {"name": "is_encashable", "label": "Is Encashable", "type": "checkbox", "required": True, "col": 6},
            {"name": "requires_attachment", "label": "Requires Attachment", "type": "checkbox", "required": True, "col": 6},
            {"name": "requires_approval", "label": "Requires Approval", "type": "checkbox", "required": True, "col": 6},
            {"name": "max_days_per_year", "label": "Max Days Per Year", "type": "number", "required": True, "col": 6},
            {"name": "color", "label": "Color", "type": "color", "required": True, "col": 6},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
            
        ],
        dynamic_sections={
            "leave_type_policy": LEAVE_TYPE_POLICY
        },
        dynamic_sections_loader=__load_leave_policy_changes,
        dynamic_sections_saver=_save_leave_policy_changes,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LEAVE_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
