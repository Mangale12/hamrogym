from __future__ import annotations

import re
from typing import Dict, List

from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.approval_workflow_data_table import (
    ApprovalWorkflowDataTableView,
    APPROVAL_WORKFLOW_COLUMNS,
)
from ...forms.approval_workflow_form import ApprovalWorkflowForm
from ...models import (
    ApprovalWorkflow,
    ApprovalWorkflowCondition,
    ApprovalWorkflowRule,
    WorkflowStep,
    WorkflowStepApprover,
    WorkflowStepCondition,
)


RULES_SECTION = {
    "title": "Approval Rules",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "condition_id",
            "label": "Condition",
            "type": "static_select",
            "options": [],
        },
        {"name": "name", "label": "Rule Name", "type": "text"},
        {"name": "description", "label": "Description", "type": "text"},
        {"name": "priority", "label": "Priority", "type": "number"},
        {
            "name": "is_active",
            "label": "Active",
            "type": "static_select",
            "options": [("1", "Yes"), ("0", "No")],
        },
    ],
}

CONDITIONS_SECTION = {
    "title": "Conditions",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "field", "label": "Field", "type": "text"},
        {
            "name": "operator",
            "label": "Operator",
            "type": "static_select",
            "options": [
                ("==", "Equals"),
                ("!=", "Not Equals"),
                (">", "Greater Than"),
                (">=", "Greater Or Equal"),
                ("<", "Less Than"),
                ("<=", "Less Or Equal"),
                ("in", "In"),
                ("not_in", "Not In"),
            ],
        },
        {"name": "value", "label": "Value", "type": "text"},
        {
            "name": "is_active",
            "label": "Active",
            "type": "static_select",
            "options": [("1", "Yes"), ("0", "No")],
        },
    ],
}

STEPS_SECTION = {
    "title": "Workflow Steps",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "step_order", "label": "Step Order", "type": "number"},
        {"name": "step_name", "label": "Step Name", "type": "text"},
        {
            "name": "approval_type",
            "label": "Approval Type",
            "type": "static_select",
            "options": WorkflowStep.APPROVAL_TYPE_CHOICES,
        },
        {"name": "min_approvals_required", "label": "Min Approvals", "type": "number"},
        {"name": "max_approvals_allowed", "label": "Max Approvals", "type": "number"},
        {
            "name": "is_parallel",
            "label": "Parallel",
            "type": "static_select",
            "options": [("1", "Yes"), ("0", "No")],
        },
        {
            "name": "allow_reject",
            "label": "Allow Reject",
            "type": "static_select",
            "options": [("1", "Yes"), ("0", "No")],
        },
        {
            "name": "allow_edit",
            "label": "Allow Edit",
            "type": "static_select",
            "options": [("1", "Yes"), ("0", "No")],
        },
        {
            "name": "allow_delegate",
            "label": "Allow Delegate",
            "type": "static_select",
            "options": [("1", "Yes"), ("0", "No")],
        },
        {"name": "timeout_hours", "label": "Timeout Hours", "type": "number"},
        {
            "name": "escalation_enabled",
            "label": "Escalation",
            "type": "static_select",
            "options": [("1", "Yes"), ("0", "No")],
        },
        {"name": "escalation_after_hours", "label": "Escalate After", "type": "number"},
        {
            "name": "escalation_type",
            "label": "Escalation Type",
            "type": "static_select",
            "options": [("", "Select")] + WorkflowStep.ESCALATION_TYPE_CHOICES,
        },
        {"name": "escalation_user_id", "label": "Escalation User ID", "type": "number"},
        {"name": "escalation_role_id", "label": "Escalation Role ID", "type": "number"},
        {
            "name": "is_final_step",
            "label": "Final Step",
            "type": "static_select",
            "options": [("1", "Yes"), ("0", "No")],
        },
    ],
}

STEP_APPROVERS_SECTION = {
    "title": "Step Approvers",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "step_id",
            "label": "Step",
            "type": "static_select",
            "options": [],
        },
        {
            "name": "approver_type",
            "label": "Approver Type",
            "type": "static_select",
            "options": WorkflowStepApprover.APPROVER_TYPE_CHOICES,
        },
        {"name": "user_id", "label": "User ID", "type": "number"},
        {"name": "role_id", "label": "Role ID", "type": "number"},
        {"name": "department_id", "label": "Department ID", "type": "number"},
        {"name": "designation_id", "label": "Designation ID", "type": "number"},
        {"name": "sequence", "label": "Sequence", "type": "number"},
        {
            "name": "is_required",
            "label": "Required",
            "type": "static_select",
            "options": [("1", "Yes"), ("0", "No")],
        },
    ],
}

STEP_CONDITIONS_SECTION = {
    "title": "Step Conditions",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "step_id",
            "label": "Step",
            "type": "static_select",
            "options": [],
        },
        {"name": "field_name", "label": "Field", "type": "text"},
        {"name": "operator", "label": "Operator", "type": "text"},
        {"name": "value", "label": "Value", "type": "text"},
    ],
}


def _parse_dynamic_section(request, section_name: str) -> List[Dict[str, object]]:
    pattern = re.compile(rf"^{re.escape(section_name)}\[(\d+)\]\[(.+)\]$")
    rows: Dict[int, Dict[str, object]] = {}

    for key, value in request.POST.items():
        match = pattern.match(key)
        if not match:
            continue
        index = int(match.group(1))
        field = match.group(2)
        rows.setdefault(index, {})[field] = value

    for key, value in request.FILES.items():
        match = pattern.match(key)
        if not match:
            continue
        index = int(match.group(1))
        field = match.group(2)
        rows.setdefault(index, {})[field] = value

    return [rows[idx] for idx in sorted(rows.keys())]


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_nullable_int(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_bool(value, default: bool = True) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    value = str(value).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


def _save_workflow_rules(request, workflow: ApprovalWorkflow) -> None:
    rows = _parse_dynamic_section(request, "rules")
    existing = {rule.id: rule for rule in ApprovalWorkflowRule.objects.filter(workflow=workflow)}
    conditions = {
        condition.id: condition
        for condition in ApprovalWorkflowCondition.objects.filter(workflow=workflow)
    }
    keep_ids = []

    for row in rows:
        rule_id = row.get("id")
        rule = None
        if rule_id and str(rule_id).isdigit():
            rule = existing.get(int(rule_id))
        if not rule:
            rule = ApprovalWorkflowRule(workflow=workflow)

        name = (row.get("name") or "").strip()
        description = (row.get("description") or "").strip()
        priority_raw = row.get("priority")
        condition_id = row.get("condition_id")

        if not name and not rule_id:
            continue
        if not condition_id or not str(condition_id).isdigit():
            continue

        condition = conditions.get(int(condition_id))
        if not condition:
            continue

        rule.name = name or rule.name or ""
        rule.description = description
        rule.priority = _to_int(priority_raw, default=0)
        rule.is_active = _to_bool(row.get("is_active"), default=True)
        rule.condition = condition
        rule.save()
        keep_ids.append(rule.id)

    if keep_ids:
        ApprovalWorkflowRule.objects.filter(workflow=workflow).exclude(id__in=keep_ids).delete()
    else:
        ApprovalWorkflowRule.objects.filter(workflow=workflow).delete()


def _save_workflow_conditions(request, workflow: ApprovalWorkflow) -> None:
    rows = _parse_dynamic_section(request, "conditions")
    existing = {
        cond.id: cond for cond in ApprovalWorkflowCondition.objects.filter(workflow=workflow)
    }
    keep_ids = []

    for row in rows:
        condition_id = row.get("id")
        condition = None
        if condition_id and str(condition_id).isdigit():
            condition = existing.get(int(condition_id))
        if not condition:
            condition = ApprovalWorkflowCondition(workflow=workflow)

        field = (row.get("field") or "").strip()
        operator = (row.get("operator") or "").strip()
        value = (row.get("value") or "").strip()

        if not field and not condition_id:
            continue

        condition.field = field or condition.field or ""
        condition.operator = operator or condition.operator or ""
        condition.value = value
        condition.is_active = _to_bool(row.get("is_active"), default=True)
        condition.save()
        keep_ids.append(condition.id)

    if keep_ids:
        ApprovalWorkflowCondition.objects.filter(workflow=workflow).exclude(id__in=keep_ids).delete()
    else:
        ApprovalWorkflowCondition.objects.filter(workflow=workflow).delete()


def _save_workflow_steps(request, workflow: ApprovalWorkflow) -> None:
    rows = _parse_dynamic_section(request, "steps")
    existing = {step.id: step for step in WorkflowStep.objects.filter(workflow=workflow)}
    keep_ids = []

    for index, row in enumerate(rows, start=1):
        step_id = row.get("id")
        step = None
        if step_id and str(step_id).isdigit():
            step = existing.get(int(step_id))
        if not step:
            step = WorkflowStep(workflow=workflow)

        step_name = (row.get("step_name") or "").strip()
        if not step_name and not step_id:
            continue

        step.step_order = _to_int(row.get("step_order"), default=index)
        step.step_name = step_name or step.step_name or ""
        step.approval_type = (
            row.get("approval_type")
            if row.get("approval_type") in dict(WorkflowStep.APPROVAL_TYPE_CHOICES)
            else WorkflowStep.APPROVAL_TYPE_ALL
        )
        step.min_approvals_required = max(1, _to_int(row.get("min_approvals_required"), default=1))
        step.max_approvals_allowed = _to_nullable_int(row.get("max_approvals_allowed"))
        step.is_parallel = _to_bool(row.get("is_parallel"), default=False)
        step.allow_reject = _to_bool(row.get("allow_reject"), default=True)
        step.allow_edit = _to_bool(row.get("allow_edit"), default=False)
        step.allow_delegate = _to_bool(row.get("allow_delegate"), default=False)
        step.timeout_hours = _to_nullable_int(row.get("timeout_hours"))
        step.escalation_enabled = _to_bool(row.get("escalation_enabled"), default=False)
        step.escalation_after_hours = _to_nullable_int(row.get("escalation_after_hours"))
        step.escalation_type = (
            row.get("escalation_type")
            if row.get("escalation_type") in dict(WorkflowStep.ESCALATION_TYPE_CHOICES)
            else ""
        )
        step.escalation_user_id = _to_nullable_int(row.get("escalation_user_id"))
        step.escalation_role_id = _to_nullable_int(row.get("escalation_role_id"))
        step.is_final_step = _to_bool(row.get("is_final_step"), default=False)
        step.save()
        keep_ids.append(step.id)

    if keep_ids:
        WorkflowStep.objects.filter(workflow=workflow).exclude(id__in=keep_ids).delete()
    else:
        WorkflowStep.objects.filter(workflow=workflow).delete()


def _save_workflow_step_approvers(request, workflow: ApprovalWorkflow) -> None:
    rows = _parse_dynamic_section(request, "step_approvers")
    existing = {
        approver.id: approver
        for approver in WorkflowStepApprover.objects.filter(step__workflow=workflow).select_related("step")
    }
    steps = {step.id: step for step in WorkflowStep.objects.filter(workflow=workflow)}
    keep_ids = []

    for row in rows:
        approver_id = row.get("id")
        approver = None
        if approver_id and str(approver_id).isdigit():
            approver = existing.get(int(approver_id))
        if not approver:
            step_ref = _to_nullable_int(row.get("step_id"))
            if not step_ref or step_ref not in steps:
                continue
            approver = WorkflowStepApprover(step=steps[step_ref])

        step_ref = _to_nullable_int(row.get("step_id"))
        approver_type = row.get("approver_type")
        if not step_ref or step_ref not in steps:
            continue
        if approver_type not in dict(WorkflowStepApprover.APPROVER_TYPE_CHOICES):
            continue

        approver.step = steps[step_ref]
        approver.approver_type = approver_type
        approver.user_id = _to_nullable_int(row.get("user_id"))
        approver.role_id = _to_nullable_int(row.get("role_id"))
        approver.department_id = _to_nullable_int(row.get("department_id"))
        approver.designation_id = _to_nullable_int(row.get("designation_id"))
        approver.sequence = _to_int(row.get("sequence"), default=1)
        approver.is_required = _to_bool(row.get("is_required"), default=True)

        has_target = any(
            [
                approver.user_id,
                approver.role_id,
                approver.department_id,
                approver.designation_id,
            ]
        )
        if not has_target:
            continue

        approver.save()
        keep_ids.append(approver.id)

    queryset = WorkflowStepApprover.objects.filter(step__workflow=workflow)
    if keep_ids:
        queryset.exclude(id__in=keep_ids).delete()
    else:
        queryset.delete()


def _save_workflow_step_conditions(request, workflow: ApprovalWorkflow) -> None:
    rows = _parse_dynamic_section(request, "step_conditions")
    existing = {
        condition.id: condition
        for condition in WorkflowStepCondition.objects.filter(step__workflow=workflow).select_related("step")
    }
    steps = {step.id: step for step in WorkflowStep.objects.filter(workflow=workflow)}
    keep_ids = []

    for row in rows:
        condition_id = row.get("id")
        condition = None
        if condition_id and str(condition_id).isdigit():
            condition = existing.get(int(condition_id))
        if not condition:
            step_ref = _to_nullable_int(row.get("step_id"))
            if not step_ref or step_ref not in steps:
                continue
            condition = WorkflowStepCondition(step=steps[step_ref])

        step_ref = _to_nullable_int(row.get("step_id"))
        field_name = (row.get("field_name") or "").strip()
        operator = (row.get("operator") or "").strip()
        value = (row.get("value") or "").strip()

        if not step_ref or step_ref not in steps or not field_name or not operator:
            continue

        condition.step = steps[step_ref]
        condition.field_name = field_name
        condition.operator = operator
        condition.value = value
        condition.save()
        keep_ids.append(condition.id)

    queryset = WorkflowStepCondition.objects.filter(step__workflow=workflow)
    if keep_ids:
        queryset.exclude(id__in=keep_ids).delete()
    else:
        queryset.delete()


def _refresh_dynamic_section_options(workflow: ApprovalWorkflow) -> None:
    condition_options = [
        (str(condition.id), str(condition))
        for condition in ApprovalWorkflowCondition.objects.filter(workflow=workflow).order_by("id")
    ]
    step_options = [
        (str(step.id), f"{step.step_order}. {step.step_name}")
        for step in WorkflowStep.objects.filter(workflow=workflow).order_by("step_order", "id")
    ]

    RULES_SECTION["fields"][0]["options"] = condition_options
    STEP_APPROVERS_SECTION["fields"][0]["options"] = step_options
    STEP_CONDITIONS_SECTION["fields"][0]["options"] = step_options


def _load_workflow_sections(workflow: ApprovalWorkflow) -> Dict[str, List[Dict[str, object]]]:
    _refresh_dynamic_section_options(workflow)
    rules = [
        {
            "id": rule.id,
            "condition_id": str(rule.condition_id or ""),
            "name": rule.name,
            "description": rule.description,
            "priority": rule.priority,
            "is_active": "1" if rule.is_active else "0",
        }
        for rule in ApprovalWorkflowRule.objects.filter(workflow=workflow).order_by("priority", "id")
    ]
    conditions = [
        {
            "id": cond.id,
            "field": cond.field,
            "operator": cond.operator,
            "value": cond.value,
            "is_active": "1" if cond.is_active else "0",
        }
        for cond in ApprovalWorkflowCondition.objects.filter(workflow=workflow).order_by("id")
    ]
    steps = [
        {
            "id": step.id,
            "step_order": step.step_order,
            "step_name": step.step_name,
            "approval_type": step.approval_type,
            "min_approvals_required": step.min_approvals_required,
            "max_approvals_allowed": step.max_approvals_allowed or "",
            "is_parallel": "1" if step.is_parallel else "0",
            "allow_reject": "1" if step.allow_reject else "0",
            "allow_edit": "1" if step.allow_edit else "0",
            "allow_delegate": "1" if step.allow_delegate else "0",
            "timeout_hours": step.timeout_hours or "",
            "escalation_enabled": "1" if step.escalation_enabled else "0",
            "escalation_after_hours": step.escalation_after_hours or "",
            "escalation_type": step.escalation_type,
            "escalation_user_id": step.escalation_user_id or "",
            "escalation_role_id": step.escalation_role_id or "",
            "is_final_step": "1" if step.is_final_step else "0",
        }
        for step in WorkflowStep.objects.filter(workflow=workflow).order_by("step_order", "id")
    ]
    step_approvers = [
        {
            "id": approver.id,
            "step_id": str(approver.step_id or ""),
            "approver_type": approver.approver_type,
            "user_id": approver.user_id or "",
            "role_id": approver.role_id or "",
            "department_id": approver.department_id or "",
            "designation_id": approver.designation_id or "",
            "sequence": approver.sequence,
            "is_required": "1" if approver.is_required else "0",
        }
        for approver in WorkflowStepApprover.objects.filter(step__workflow=workflow).order_by(
            "step__step_order", "sequence", "id"
        )
    ]
    step_conditions = [
        {
            "id": condition.id,
            "step_id": str(condition.step_id or ""),
            "field_name": condition.field_name,
            "operator": condition.operator,
            "value": condition.value,
        }
        for condition in WorkflowStepCondition.objects.filter(step__workflow=workflow).order_by("id")
    ]
    return {
        "rules": rules,
        "conditions": conditions,
        "steps": steps,
        "step_approvers": step_approvers,
        "step_conditions": step_conditions,
    }


def _save_workflow_sections(request, workflow: ApprovalWorkflow) -> None:
    _save_workflow_conditions(request, workflow)
    _save_workflow_steps(request, workflow)
    _save_workflow_step_conditions(request, workflow)
    _save_workflow_step_approvers(request, workflow)
    _refresh_dynamic_section_options(workflow)
    _save_workflow_rules(request, workflow)


register_entity(
    EntityConfig(
        name="approval_workflow",
        url_path="approval-workflows",
        verbose_name="Approval Workflow",
        model=ApprovalWorkflow,
        form_class=ApprovalWorkflowForm,
        datatable_view=ApprovalWorkflowDataTableView,
        fields=[],
        tabs=[
            {
                "key": "workflow",
                "label": "Workflow",
                "fields": [
                    {
                        "name": "entity",
                        "label": "Approval Entity",
                        "type": "select",
                        "required": True,
                        "col": 6,
                        "url_name": "approval_entities_select",
                    },
                    {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
                    {"name": "code", "label": "Code", "type": "text", "required": True, "col": 4},
                    {
                        "name": "priority",
                        "label": "Priority",
                        "type": "number",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "version",
                        "label": "Version",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "is_default",
                        "label": "Default",
                        "type": "checkbox",
                        "required": False,
                        "col": 3,
                    },
                    {
                        "name": "is_active",
                        "label": "Active",
                        "type": "checkbox",
                        "required": False,
                        "col": 3,
                    },
                    {
                        "name": "effective_from",
                        "label": "Effective From",
                        "type": "datetime",
                        "required": False,
                        "col": 3,
                    },
                    {
                        "name": "effective_to",
                        "label": "Effective To",
                        "type": "datetime",
                        "required": False,
                        "col": 3,
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
            },
            {
                "key": "steps",
                "label": "Steps",
                "fields": [],
                "sections": ["steps"],
                "requires_id": True,
            },
            {
                "key": "step_approvers",
                "label": "Step Approvers",
                "fields": [],
                "sections": ["step_approvers"],
                "requires_id": True,
            },
            {
                "key": "step_conditions",
                "label": "Step Conditions",
                "fields": [],
                "sections": ["step_conditions"],
                "requires_id": True,
            },
            {
                "key": "conditions",
                "label": "Conditions",
                "fields": [],
                "sections": ["conditions"],
                "requires_id": True,
            },
            {
                "key": "rules",
                "label": "Rules",
                "fields": [],
                "sections": ["rules"],
                "requires_id": True,
            },
        ],
        dynamic_sections={
            "rules": RULES_SECTION,
            "conditions": CONDITIONS_SECTION,
            "steps": STEPS_SECTION,
            "step_approvers": STEP_APPROVERS_SECTION,
            "step_conditions": STEP_CONDITIONS_SECTION,
        },
        dynamic_sections_loader=_load_workflow_sections,
        dynamic_sections_saver=_save_workflow_sections,
        action_buttons=[
            {
                "title": "Manage Conditions",
                "label": "",
                "tab_key": "conditions",
                "icon_class": "fas fa-sitemap",
                "class_name": "btn-outline-info",
                "button_class": "open-tab-btn",
            },
        ],
        datatable_columns=[
            (
                {
                    "name": key,
                    "title": {
                        "entity": "Approval Entity",
                        "is_default": "Default",
                        "effective_from": "Effective From",
                        "effective_to": "Effective To",
                        "is_active": "Active",
                    }.get(key, key.replace("_", " ").title()),
                    "render": "function(data){return data ? 'Yes' : 'No';}"
                    if key in {"is_default", "is_active"}
                    else None,
                }
            )
            for key, _accessor in APPROVAL_WORKFLOW_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
    )
)
