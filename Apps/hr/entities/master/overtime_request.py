from decimal import Decimal

from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.overtime_request_data_table import (
    OVERTIME_REQUEST_COLUMNS,
    OvertimeRequestDataTableView,
)
from ...forms.overtime_form import OvertimeRequestForm
from ...models import Employee, OvertimeRecord, OvertimeRequest
from ...services import apply_policies, build_policy_context


def _calculate_hours(start_time, end_time):
    if not start_time or not end_time:
        return None
    start_minutes = (start_time.hour * 60) + start_time.minute
    end_minutes = (end_time.hour * 60) + end_time.minute
    if end_minutes <= start_minutes:
        return None
    hours = Decimal(end_minutes - start_minutes) / Decimal("60")
    return hours.quantize(Decimal("0.01"))


def _save_request(request, overtime_request: OvertimeRequest) -> None:
    employee = Employee.objects.get(pk=request.POST.get("employee"))
    update_fields = {"updated_at"}

    if overtime_request.employee_id != employee.id:
        overtime_request.employee = employee
        update_fields.add("employee")

    calculated_hours = _calculate_hours(
        overtime_request.start_time,
        overtime_request.end_time,
    )
    if overtime_request.requested_hours != calculated_hours:
        overtime_request.requested_hours = calculated_hours
        update_fields.add("requested_hours")

    if overtime_request.status != "pending":
        overtime_request.status = "pending"
        update_fields.add("status")

    if not overtime_request.requested_by_id:
        overtime_request.requested_by = request.user
        update_fields.add("requested_by")

    if len(update_fields) > 1:
        overtime_request.save(update_fields=sorted(update_fields))


def _post_save_request(request, overtime_request: OvertimeRequest) -> None:
    _save_request(request, overtime_request)
    overtime_request.refresh_from_db()
    policy_result = _apply_overtime_request_policies(overtime_request, event="request_create")
    if not policy_result["changed_fields"]:
        return
    update_fields = {"updated_at"}
    update_fields.update(policy_result["changed_fields"])
    overtime_request.save(update_fields=sorted(update_fields))


def _resolve_overtime_rate(employee: Employee):
    payroll = getattr(employee, "payroll", None)
    return getattr(payroll, "overtime_rate", None) if payroll else None


def _apply_overtime_request_policies(overtime_request: OvertimeRequest, *, event: str):
    context = build_policy_context(
        employee=overtime_request.employee,
        overtime_request=overtime_request,
        event=event,
    )
    return apply_policies(
        module="overtime",
        event=event,
        context=context,
        instance=overtime_request,
    )


def _apply_overtime_record_policies(overtime_record: OvertimeRecord, *, event: str):
    context = build_policy_context(
        employee=overtime_record.employee,
        overtime_record=overtime_record,
        event=event,
    )
    return apply_policies(
        module="overtime",
        event=event,
        context=context,
        instance=overtime_record,
    )


def _approve_request(request, overtime_request: OvertimeRequest):
    overtime_request.status = "approved"
    overtime_request.approved_by = request.user
    request_policy_result = _apply_overtime_request_policies(overtime_request, event="request_approve")
    request_update_fields = {"status", "approved_by", "updated_at"}
    request_update_fields.update(request_policy_result["changed_fields"])
    overtime_request.save(update_fields=sorted(request_update_fields))

    overtime_rate = _resolve_overtime_rate(overtime_request.employee)
    overtime_amount = None
    if overtime_rate is not None and overtime_request.requested_hours is not None:
        overtime_amount = (Decimal(overtime_rate) * Decimal(overtime_request.requested_hours)).quantize(
            Decimal("0.01")
        )

    overtime_record, _ = OvertimeRecord.objects.update_or_create(
        request=overtime_request,
        defaults={
            "employee": overtime_request.employee,
            "fiscal_year": overtime_request.fiscal_year,
            "overtime_date": overtime_request.overtime_date,
            "start_time": overtime_request.start_time,
            "end_time": overtime_request.end_time,
            "overtime_hours": overtime_request.requested_hours or Decimal("0.00"),
            "overtime_rate": overtime_rate,
            "overtime_amount": overtime_amount,
            "status": "approved",
            "remarks": overtime_request.remarks,
        },
    )
    record_policy_result = _apply_overtime_record_policies(overtime_record, event="record_create")
    record_update_fields = {"updated_at"}
    record_update_fields.update(record_policy_result["changed_fields"])
    if record_policy_result["changed_fields"]:
        overtime_record.save(update_fields=sorted(record_update_fields))
    return {"message": "Overtime request approved successfully."}


def _reject_request(request, overtime_request: OvertimeRequest):
    overtime_request.status = "rejected"
    overtime_request.approved_by = request.user
    overtime_request.save(update_fields=["status", "approved_by", "updated_at"])
    OvertimeRecord.objects.filter(request=overtime_request).delete()
    return {"message": "Overtime request rejected successfully."}


register_entity(
    EntityConfig(
        name="overtime_request",
        url_path="overtime-requests",
        verbose_name="Overtime Request",
        model=OvertimeRequest,
        form_class=OvertimeRequestForm,
        datatable_view=OvertimeRequestDataTableView,
        fields=[
            {
                "name": "employee",
                "label": "Employee",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "employee_select",
            },
            {
                "name": "overtime_date",
                "label": "Overtime Date",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {
                "name": "start_time",
                "label": "Start Time",
                "type": "time",
                "required": True,
                "col": 6,
            },
            {
                "name": "end_time",
                "label": "End Time",
                "type": "time",
                "required": True,
                "col": 6,
            },
            {
                "name": "reason",
                "label": "Reason",
                "type": "textarea",
                "required": True,
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
        post_save=_post_save_request,
        row_actions={
            "approve": _approve_request,
            "reject": _reject_request,
        },
        action_state_field="status",
        hide_edit_on_values=["approved", "rejected"],
        hide_delete_on_values=["approved"],
        action_buttons=[
            {
                "action_name": "approve",
                "title": "Approve Request",
                "label": "",
                "icon_class": "fas fa-check",
                "class_name": "btn-outline-success",
                "confirm_text": "Approve this overtime request?",
                "success_message": "Overtime request approved successfully.",
                "hide_on_values": ["approved", "rejected"],
            },
            {
                "action_name": "reject",
                "title": "Reject Request",
                "label": "",
                "icon_class": "fas fa-times",
                "class_name": "btn-outline-danger",
                "confirm_text": "Reject this overtime request?",
                "success_message": "Overtime request rejected successfully.",
                "hide_on_values": ["approved", "rejected"],
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in OVERTIME_REQUEST_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "overtime_date": timezone.localdate().isoformat(),
        },
        select_search_fields=[
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "status",
            "reason",
        ],
    )
)
