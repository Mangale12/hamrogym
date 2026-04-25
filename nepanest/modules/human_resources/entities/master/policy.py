from django.contrib.contenttypes.models import ContentType

from core.choices import MODULE_CHOICES
from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
    parse_dynamic_section,
)
from nepanest.modules.attendance.models import Shift
from nepanest.modules.people.models import Department, Employee
from nepanest.modules.policies.datatables import POLICY_COLUMNS, PolicyDataTableView
from nepanest.modules.policies.forms import PolicyForm
from nepanest.modules.policies.models import Policy, PolicyAction, PolicyCondition, PolicyScope


CONDITIONS_SECTION = {
    "title": "Policy Conditions",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "field_name",
            "label": "Field",
            "type": "static_select",
            "required": True,
            "options": PolicyCondition.FIELD_CHOICES,
        },
        {
            "name": "operator",
            "label": "Operator",
            "type": "static_select",
            "required": True,
            "options": PolicyCondition.OPERATOR_CHOICES,
        },
        {
            "name": "value",
            "label": "Value",
            "type": "text",
            "required": False,
        },
        {
            "name": "logical_operator",
            "label": "Logical",
            "type": "static_select",
            "required": True,
            "options": PolicyCondition.LOGICAL_OPERATOR_CHOICES,
        },
        {
            "name": "sequence",
            "label": "Sequence",
            "type": "number",
            "required": False,
            "min": 1,
        },
        {
            "name": "is_active",
            "label": "Active",
            "type": "checkbox",
            "required": False,
        },
    ],
}


SCOPES_SECTION = {
    "title": "Policy Scopes",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "department_id",
            "label": "Department",
            "type": "select",
            "required": False,
            "url_name": "department_select",
        },
        {
            "name": "employee_id",
            "label": "Employee",
            "type": "select",
            "required": False,
            "url_name": "employee_select",
        },
        {
            "name": "shift_id",
            "label": "Shift",
            "type": "select",
            "required": False,
            "url_name": "shift_select",
        },
        {
            "name": "is_active",
            "label": "Active",
            "type": "checkbox",
            "required": False,
        },
    ],
}


ACTIONS_SECTION = {
    "title": "Policy Actions",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "action_type",
            "label": "Action Type",
            "type": "static_select",
            "required": True,
            "options": PolicyAction.ACTION_CHOICES,
        },
        {
            "name": "target_field",
            "label": "Target Field",
            "type": "static_select",
            "required": False,
            "options": [("", "---------")] + list(PolicyAction.TARGET_FIELD_CHOICES),
        },
        {
            "name": "action_value",
            "label": "Action Value",
            "type": "text",
            "required": False,
        },
        {
            "name": "sequence",
            "label": "Sequence",
            "type": "number",
            "required": False,
            "min": 1,
        },
        {
            "name": "is_active",
            "label": "Active",
            "type": "checkbox",
            "required": False,
        },
    ],
}


CONDITION_RELATION = RelatedDynamicSectionConfig(
    section_name="conditions",
    related_model=PolicyCondition,
    parent_field="policy",
    fields=["field_name", "operator", "value", "logical_operator", "sequence", "is_active"],
    required_fields=["field_name", "operator"],
    bool_fields=["is_active"],
    empty_check_fields=["field_name", "operator", "value", "logical_operator", "sequence", "is_active"],
    order_by="sequence",
    save_transformers={
        "field_name": lambda value: (value or "").strip(),
        "operator": lambda value: (value or "").strip(),
        "value": lambda value: (value or "").strip(),
        "logical_operator": lambda value: (value or "").strip() or PolicyCondition.LOGICAL_AND,
        "sequence": lambda value: _to_int(value, default=1),
    },
)


_load_conditions = build_related_section_loader(CONDITION_RELATION)
_save_conditions = build_related_section_saver(CONDITION_RELATION)


ACTION_RELATION = RelatedDynamicSectionConfig(
    section_name="actions",
    related_model=PolicyAction,
    parent_field="policy",
    fields=["action_type", "target_field", "action_value", "sequence", "is_active"],
    required_fields=["action_type"],
    bool_fields=["is_active"],
    empty_check_fields=["action_type", "target_field", "action_value", "sequence", "is_active"],
    order_by="sequence",
    save_transformers={
        "action_type": lambda value: (value or "").strip(),
        "target_field": lambda value: (value or "").strip(),
        "action_value": lambda value: (value or "").strip(),
        "sequence": lambda value: _to_int(value, default=1),
    },
)


_load_actions = build_related_section_loader(ACTION_RELATION)
_save_actions = build_related_section_saver(ACTION_RELATION)


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _save_policy_scopes(request, parent_obj) -> None:
    rows = parse_dynamic_section(request, "scopes")
    keep_ids = []
    existing_ids = []

    for row in rows:
        if not any(row.get(field) for field in ("department_id", "employee_id", "shift_id")):
            continue

        is_active = str(row.get("is_active") or "").strip().lower() in {"1", "true", "yes", "on"}
        targets = [
            (Department, row.get("department_id")),
            (Employee, row.get("employee_id")),
            (Shift, row.get("shift_id")),
        ]

        for model, object_id in targets:
            if not object_id:
                continue
            content_type = ContentType.objects.get_for_model(model)
            scope, _ = PolicyScope.objects.get_or_create(
                policy=parent_obj,
                content_type=content_type,
                object_id=int(object_id),
                defaults={"is_active": is_active},
            )
            if scope.is_active != is_active:
                scope.is_active = is_active
                scope.save(update_fields=["is_active", "updated_at"])
            keep_ids.append(scope.id)

    existing_ids = list(
        PolicyScope.objects.filter(policy=parent_obj).values_list("id", flat=True)
    )
    stale_ids = [scope_id for scope_id in existing_ids if scope_id not in keep_ids]
    if stale_ids:
        PolicyScope.objects.filter(id__in=stale_ids).delete()
    elif not keep_ids:
        PolicyScope.objects.filter(policy=parent_obj).delete()


def _load_policy_scopes(parent_obj):
    rows = []
    department_type = ContentType.objects.get_for_model(Department)
    employee_type = ContentType.objects.get_for_model(Employee)
    shift_type = ContentType.objects.get_for_model(Shift)

    for scope in PolicyScope.objects.filter(policy=parent_obj).select_related("content_type").order_by("id"):
        row = {
            "id": scope.id,
            "department_id": "",
            "employee_id": "",
            "shift_id": "",
            "is_active": scope.is_active,
        }
        if scope.content_type_id == department_type.id:
            row["department_id"] = str(scope.object_id)
        elif scope.content_type_id == employee_type.id:
            row["employee_id"] = str(scope.object_id)
        elif scope.content_type_id == shift_type.id:
            row["shift_id"] = str(scope.object_id)
        rows.append(row)
    return {"scopes": rows}


def _load_policy_dynamic_sections(parent_obj):
    data = {}
    data.update(_load_conditions(parent_obj))
    data.update(_load_actions(parent_obj))
    data.update(_load_policy_scopes(parent_obj))
    return data


def _save_policy_dynamic_sections(request, parent_obj):
    _save_conditions(request, parent_obj)
    _save_actions(request, parent_obj)
    _save_policy_scopes(request, parent_obj)


register_entity(
    EntityConfig(
        name="policy",
        url_path="policies",
        verbose_name="Policies",
        model=Policy,
        form_class=PolicyForm,
        datatable_view=PolicyDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {
                "name": "module",
                "label": "Module",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": MODULE_CHOICES,
            },
            {
                "name": "trigger_event",
                "label": "Trigger Event",
                "type": "static_select",
                "required": False,
                "col": 4,
                "options": [
                    ("", "All Events"),
                    ("check_in", "Check In"),
                    ("check_out", "Check Out"),
                    ("request_create", "Overtime Request Create"),
                    ("request_approve", "Overtime Request Approve"),
                    ("record_create", "Overtime Record Create"),
                ],
            },
            {"name": "priority", "label": "Priority", "type": "number", "col": 4},
            {"name": "effective_from", "label": "Effective From", "type": "date", "col": 6},
            {"name": "effective_to", "label": "Effective To", "type": "date", "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "col": 4},
            {"name": "description", "label": "Description", "type": "textarea", "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "col": 12},
        ],
        dynamic_sections={
            "conditions": CONDITIONS_SECTION,
            "actions": ACTIONS_SECTION,
            "scopes": SCOPES_SECTION,
        },
        dynamic_sections_loader=_load_policy_dynamic_sections,
        dynamic_sections_saver=_save_policy_dynamic_sections,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in POLICY_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True, "priority": 1, "module": "attendance"},
        select_search_fields=["name", "code", "module", "description"],
    )
)
