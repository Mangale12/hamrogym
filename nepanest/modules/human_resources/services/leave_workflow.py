from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from nepanest.common.helpers.context import get_current_fiscal_year_id
from nepanest.modules.attendance.models import Attendance
from nepanest.modules.leave.models import LeaveApproval, LeaveRequest

from nepanest.modules.human_resources.services.leave_balance import consume_leave_balance, reverse_leave_balance
from nepanest.modules.human_resources.services.leave_calculator import validate_leave_request


def sync_leave_request_values(leave_request: LeaveRequest):
    result = validate_leave_request(
        employee=leave_request.employee,
        leave_type=leave_request.leave_type,
        start_date=leave_request.start_date,
        end_date=leave_request.end_date,
        is_half_day=leave_request.is_half_day,
        leave_request=leave_request,
    )
    leave_request.total_days = result["total_days"]
    return result


def _attendance_remarks(leave_request: LeaveRequest) -> str:
    return f"Leave: {leave_request.leave_type} ({leave_request.status})"


def _sync_attendance_rows(*, leave_request: LeaveRequest, request=None):
    fiscal_year_id = get_current_fiscal_year_id(request) if request is not None else None
    calculation = validate_leave_request(
        employee=leave_request.employee,
        leave_type=leave_request.leave_type,
        start_date=leave_request.start_date,
        end_date=leave_request.end_date,
        is_half_day=leave_request.is_half_day,
        leave_request=leave_request,
    )
    leave_dates = calculation["leave_dates"]
    for leave_date in leave_dates:
        attendance, _created = Attendance.objects.get_or_create(
            employee=leave_request.employee,
            date=leave_date,
            defaults={"fiscal_year_id": fiscal_year_id},
        )
        if fiscal_year_id and not attendance.fiscal_year_id:
            attendance.fiscal_year_id = fiscal_year_id
        attendance.status = "leave"
        attendance.is_half_day = bool(leave_request.is_half_day and leave_request.start_date == leave_date)
        attendance.remarks = _attendance_remarks(leave_request)
        attendance.save(update_fields=["fiscal_year", "status", "is_half_day", "remarks", "updated_at"])


def _revert_attendance_rows(*, leave_request: LeaveRequest):
    calculation = validate_leave_request(
        employee=leave_request.employee,
        leave_type=leave_request.leave_type,
        start_date=leave_request.start_date,
        end_date=leave_request.end_date,
        is_half_day=leave_request.is_half_day,
        leave_request=leave_request,
    )
    Attendance.objects.filter(
        employee=leave_request.employee,
        date__in=calculation["leave_dates"],
        status="leave",
    ).update(status="pending", is_half_day=False, remarks="")


def _approval_chain_for_employee(employee, max_levels: int = 5):
    approvers = []
    seen_user_ids = set()
    current_manager = employee.reporting_manager

    while current_manager is not None and len(approvers) < max_levels:
        user_id = getattr(current_manager, "user_id", None)
        if not user_id or user_id in seen_user_ids:
            break
        approvers.append(current_manager.user)
        seen_user_ids.add(user_id)
        current_manager = current_manager.reporting_manager

    return approvers


def _ensure_leave_approvals(leave_request: LeaveRequest):
    if not leave_request.leave_type.requires_approval:
        LeaveApproval.objects.filter(leave_request=leave_request).delete()
        return []

    existing = list(LeaveApproval.objects.filter(leave_request=leave_request).order_by("level", "id"))
    if existing:
        return existing

    approvers = _approval_chain_for_employee(leave_request.employee)
    if not approvers:
        raise ValidationError({"employee": "No reporting-manager approval chain found for this employee."})

    approvals = [
        LeaveApproval(
            leave_request=leave_request,
            approver=approver,
            level=index,
            status="pending",
        )
        for index, approver in enumerate(approvers, start=1)
    ]
    created = LeaveApproval.objects.bulk_create(approvals)
    return created


def _pending_approval(leave_request: LeaveRequest):
    return leave_request.approvals.filter(status="pending").order_by("level", "id").first()


def _finalize_leave_approval(*, leave_request: LeaveRequest, acting_user, request=None):
    leave_request.status = "approved"
    leave_request.approved_at = timezone.now()
    leave_request.cancelled_at = None
    leave_request.approved_by = acting_user
    leave_request.rejected_by = None
    leave_request.save(
        update_fields=[
            "total_days",
            "status",
            "approved_at",
            "cancelled_at",
            "approved_by",
            "rejected_by",
            "updated_at",
        ]
    )
    consume_leave_balance(leave_request=leave_request)
    _sync_attendance_rows(leave_request=leave_request, request=request)


def _reset_approval_rows(*, leave_request: LeaveRequest, keep_status: str):
    leave_request.approvals.exclude(status=keep_status).update(
        status="cancelled",
        action_at=timezone.now(),
    )


@transaction.atomic
def prepare_leave_request(*, leave_request: LeaveRequest):
    result = sync_leave_request_values(leave_request)
    if leave_request.leave_type.requires_attachment and not leave_request.attachment:
        raise ValidationError({"attachment": "Attachment is required for this leave type."})
    if leave_request.status not in {"approved", "rejected", "cancelled"}:
        leave_request.status = "pending"
    _ensure_leave_approvals(leave_request)
    return result


@transaction.atomic
def approve_leave_request(*, leave_request: LeaveRequest, acting_user, request=None):
    if leave_request.status == "approved":
        raise ValidationError("This leave request is already approved.")
    prepare_leave_request(leave_request=leave_request)
    if not leave_request.leave_type.requires_approval:
        _finalize_leave_approval(leave_request=leave_request, acting_user=acting_user, request=request)
        return {"finalized": True, "level": None}

    pending_approval = _pending_approval(leave_request)
    if pending_approval is None:
        raise ValidationError("This leave request has no pending approval step.")
    if pending_approval.approver_id != acting_user.id:
        raise ValidationError("You are not the current approver for this leave request.")

    pending_approval.status = "approved"
    pending_approval.action_at = timezone.now()
    pending_approval.save(update_fields=["status", "action_at"])

    next_pending = _pending_approval(leave_request)
    if next_pending is not None:
        leave_request.status = "pending"
        leave_request.approved_by = None
        leave_request.approved_at = None
        leave_request.rejected_by = None
        leave_request.cancelled_at = None
        leave_request.save(
            update_fields=["status", "approved_by", "approved_at", "rejected_by", "cancelled_at", "updated_at"]
        )
        return {"finalized": False, "level": pending_approval.level, "next_level": next_pending.level}

    _finalize_leave_approval(leave_request=leave_request, acting_user=acting_user, request=request)
    return {"finalized": True, "level": pending_approval.level}


@transaction.atomic
def reject_leave_request(*, leave_request: LeaveRequest, acting_user):
    prepare_leave_request(leave_request=leave_request)
    pending_approval = _pending_approval(leave_request)
    if leave_request.leave_type.requires_approval:
        if pending_approval is None:
            raise ValidationError("This leave request has no pending approval step.")
        if pending_approval.approver_id != acting_user.id:
            raise ValidationError("You are not the current approver for this leave request.")
        pending_approval.status = "rejected"
        pending_approval.action_at = timezone.now()
        pending_approval.save(update_fields=["status", "action_at"])
        _reset_approval_rows(leave_request=leave_request, keep_status="rejected")

    if leave_request.status == "approved":
        _revert_attendance_rows(leave_request=leave_request)
        reverse_leave_balance(leave_request=leave_request, remarks="Leave rejected after prior approval.")
    leave_request.status = "rejected"
    leave_request.rejected_by = acting_user
    leave_request.approved_by = None
    leave_request.approved_at = None
    leave_request.cancelled_at = None
    leave_request.save(
        update_fields=[
            "status",
            "rejected_by",
            "approved_by",
            "approved_at",
            "cancelled_at",
            "updated_at",
        ]
    )
    return {"finalized": True, "level": getattr(pending_approval, "level", None)}


@transaction.atomic
def cancel_leave_request(*, leave_request: LeaveRequest):
    if leave_request.status == "approved":
        _revert_attendance_rows(leave_request=leave_request)
        reverse_leave_balance(leave_request=leave_request, remarks="Leave cancelled.")
    leave_request.approvals.filter(status="pending").update(status="cancelled", action_at=timezone.now())
    leave_request.status = "cancelled"
    leave_request.cancelled_at = timezone.now()
    leave_request.save(update_fields=["status", "cancelled_at", "updated_at"])
