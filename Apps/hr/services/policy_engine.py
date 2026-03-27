import json
from datetime import date, datetime, time
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, Q
from django.utils import timezone

from Apps.hr.models import Policy, PolicyAction, PolicyCondition, PolicyScope


def build_policy_context(
    *,
    employee=None,
    attendance=None,
    shift=None,
    overtime_request=None,
    overtime_record=None,
    event=None,
    extra=None,
):
    context = {
        "employee": employee,
        "attendance": attendance,
        "shift": shift,
        "overtime_request": overtime_request,
        "overtime_record": overtime_record,
        "event": event,
        "today": timezone.localdate(),
    }

    if employee is not None:
        context.update(
            {
                "employee_id": employee.pk,
                "employee_code": employee.employee_code,
                "department": employee.department,
                "department_id": employee.department_id,
                "designation": employee.designation,
                "designation_id": employee.designation_id,
                "employee_type": employee.employee_type,
                "employment_status": employee.employment_status,
            }
        )

    if attendance is not None:
        context.update(
            {
                "attendance_id": attendance.pk,
                "attendance_date": attendance.date,
                "attendance_status": attendance.status,
                "check_in_time": attendance.check_in_time,
                "check_out_time": attendance.check_out_time,
                "is_late": attendance.is_late,
                "is_half_day": attendance.is_half_day,
            }
        )

    if shift is not None:
        context.update(
            {
                "shift_id": shift.pk,
                "shift_name": shift.name,
                "shift_code": shift.code,
                "shift_start_time": shift.start_time,
                "shift_end_time": shift.end_time,
                "grace_start_time": shift.grace_start_time,
                "grace_end_time": shift.grace_end_time,
            }
        )

    if attendance is not None and attendance.date:
        context["weekday"] = attendance.date.strftime("%A").lower()

    if overtime_request is not None:
        context.update(
            {
                "overtime_date": overtime_request.overtime_date,
                "overtime_start_time": overtime_request.start_time,
                "overtime_end_time": overtime_request.end_time,
                "overtime_status": overtime_request.status,
                "requested_hours": overtime_request.requested_hours,
            }
        )

    if overtime_record is not None:
        context.update(
            {
                "overtime_date": overtime_record.overtime_date,
                "overtime_start_time": overtime_record.start_time,
                "overtime_end_time": overtime_record.end_time,
                "overtime_status": overtime_record.status,
                "overtime_hours": overtime_record.overtime_hours,
                "overtime_rate": overtime_record.overtime_rate,
                "overtime_amount": overtime_record.overtime_amount,
            }
        )

    overtime_source = overtime_request or overtime_record
    if overtime_source is not None and overtime_source.overtime_date:
        context["weekday"] = overtime_source.overtime_date.strftime("%A").lower()

    if extra:
        context.update(extra)

    return context


def apply_policies(*, module, event="", context=None, instance=None):
    context = context or {}
    today = timezone.localdate()
    matched_policies = []
    applied_actions = []
    changed_fields = set()

    policies = (
        Policy.objects.filter(module=module, is_active=True)
        .filter(Q(effective_from__isnull=True) | Q(effective_from__lte=today))
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
        .filter(Q(trigger_event="") | Q(trigger_event=event))
        .prefetch_related(
            Prefetch("conditions", queryset=PolicyCondition.objects.filter(is_active=True).order_by("sequence", "id")),
            Prefetch("actions", queryset=PolicyAction.objects.filter(is_active=True).order_by("sequence", "id")),
            Prefetch("scopes", queryset=PolicyScope.objects.filter(is_active=True).select_related("content_type")),
        )
        .order_by("-priority", "name")
    )

    for policy in policies:
        if not _policy_matches_scope(policy, context):
            continue
        if not _conditions_match(policy, context):
            continue

        matched_policies.append(policy)
        for action in policy.actions.all():
            action_changes = _apply_action(action, instance=instance)
            if action_changes:
                changed_fields.update(action_changes)
                applied_actions.append(action)

    return {
        "matched_policies": matched_policies,
        "applied_actions": applied_actions,
        "changed_fields": sorted(changed_fields),
    }


def _policy_matches_scope(policy, context):
    scopes = list(policy.scopes.all())
    if not scopes:
        return True

    candidates = _scope_candidates_from_context(context)
    return any((scope.content_type_id, scope.object_id) in candidates for scope in scopes)


def _scope_candidates_from_context(context):
    candidates = set()
    for key in ("employee", "department", "shift", "attendance", "overtime_request", "overtime_record"):
        value = context.get(key)
        if value is not None:
            _register_scope_candidate(value, candidates)

    employee = context.get("employee")
    if employee is not None:
        if employee.department_id:
            _register_scope_candidate(employee.department, candidates)

    attendance = context.get("attendance")
    if attendance is not None and getattr(attendance, "shift_id", None):
        _register_scope_candidate(attendance.shift, candidates)

    return candidates


def _register_scope_candidate(obj, candidates):
    if obj is None or getattr(obj, "pk", None) is None:
        return
    content_type = ContentType.objects.get_for_model(obj, for_concrete_model=False)
    candidates.add((content_type.pk, obj.pk))


def _conditions_match(policy, context):
    conditions = list(policy.conditions.all())
    if not conditions:
        return True

    result = None
    for condition in conditions:
        current = _evaluate_condition(condition, context)
        if result is None:
            result = current
            continue

        if condition.logical_operator == PolicyCondition.LOGICAL_OR:
            result = result or current
        else:
            result = result and current

    return bool(result)


def _evaluate_condition(condition, context):
    left = _resolve_value(context, condition.field_name)
    right = _parse_condition_value(condition.value)
    operator = (condition.operator or "eq").strip().lower()

    if operator in {"eq", "=", "=="}:
        return left == right
    if operator in {"neq", "!=", "<>"}:
        return left != right
    if operator == "gt":
        return _safe_compare(left, right, lambda a, b: a > b)
    if operator == "gte":
        return _safe_compare(left, right, lambda a, b: a >= b)
    if operator == "lt":
        return _safe_compare(left, right, lambda a, b: a < b)
    if operator == "lte":
        return _safe_compare(left, right, lambda a, b: a <= b)
    if operator == "in":
        values = right if isinstance(right, (list, tuple, set)) else [right]
        return left in values
    if operator == "not_in":
        values = right if isinstance(right, (list, tuple, set)) else [right]
        return left not in values
    if operator == "contains":
        return str(right) in str(left or "")
    if operator == "is_true":
        return bool(left) is True
    if operator == "is_false":
        return bool(left) is False
    if operator == "is_null":
        return left is None
    if operator == "not_null":
        return left is not None
    return False


def _resolve_value(source, path):
    value = source
    for part in path.split("."):
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get(part)
        else:
            value = getattr(value, part, None)
    return value


def _parse_condition_value(raw_value):
    if raw_value in ("", None):
        return raw_value

    if isinstance(raw_value, (list, dict, bool, int, float, Decimal, date, datetime, time)):
        return raw_value

    text = str(raw_value).strip()
    lowered = text.lower()

    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    for parser in (int, float, Decimal):
        try:
            return parser(text)
        except Exception:
            continue

    return text


def _safe_compare(left, right, comparator):
    try:
        return comparator(left, right)
    except TypeError:
        return False


def _apply_action(action, *, instance=None):
    if instance is None:
        return set()

    changed_fields = set()

    if action.action_type == PolicyAction.ACTION_SET_FIELD:
        if not action.target_field:
            return changed_fields
        new_value = _coerce_model_value(instance, action.target_field, action.action_value)
        if _set_instance_value(instance, action.target_field, new_value):
            changed_fields.add(action.target_field)
        return changed_fields

    if action.action_type == PolicyAction.ACTION_APPEND_REMARK:
        remarks = (getattr(instance, "remarks", "") or "").strip()
        addition = str(action.action_value or "").strip()
        if addition:
            setattr(instance, "remarks", f"{remarks} {addition}".strip() if remarks else addition)
            changed_fields.add("remarks")
        return changed_fields

    if action.action_type == PolicyAction.ACTION_MARK_LATE:
        if _set_instance_value(instance, "status", "late"):
            changed_fields.add("status")
        if hasattr(instance, "is_late") and _set_instance_value(instance, "is_late", True):
            changed_fields.add("is_late")
        return changed_fields

    if action.action_type == PolicyAction.ACTION_MARK_HALF_DAY:
        if _set_instance_value(instance, "status", "half_day"):
            changed_fields.add("status")
        if hasattr(instance, "is_half_day") and _set_instance_value(instance, "is_half_day", True):
            changed_fields.add("is_half_day")
        return changed_fields

    if action.action_type == PolicyAction.ACTION_SET_STATUS:
        if _set_instance_value(instance, "status", str(action.action_value or "").strip()):
            changed_fields.add("status")
        return changed_fields

    return changed_fields


def _coerce_model_value(instance, field_name, value):
    try:
        field = instance._meta.get_field(field_name)
    except Exception:
        return _parse_condition_value(value)

    if hasattr(field, "to_python"):
        return field.to_python(_parse_condition_value(value))
    return _parse_condition_value(value)


def _set_instance_value(instance, field_name, value):
    current_value = getattr(instance, field_name, None)
    if current_value == value:
        return False
    setattr(instance, field_name, value)
    return True
