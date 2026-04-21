from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.attendance_adjustment_data_table import (
    ATTENDANCE_ADJUSTMENT_COLUMNS,
    AttendanceAdjustmentDataTableView,
)
from ...forms.attendance_form import AttendanceAdjustmentForm
from ...models import Attendance, AttendanceAdjustment, Employee
from ...services import resolve_employee_shift


def _derive_attendance_status(employee: Employee, check_in_time):
    if not check_in_time:
        return "pending"
    shift = resolve_employee_shift(employee)
    if not shift or not shift.grace_end_time:
        return "present"
    return "late" if check_in_time > shift.grace_end_time else "present"


def _save_adjustment(request, adjustment: AttendanceAdjustment) -> None:
    employee = Employee.objects.get(pk=request.POST.get("employee"))
    attendance_date = request.POST.get("attendance_date")
    attendance, _ = Attendance.objects.get_or_create(
        employee=employee,
        date=attendance_date,
        defaults={"status": "pending"},
    )
    adjustment.attendance = attendance
    if not adjustment.pk and not adjustment.requested_by_id:
        adjustment.requested_by = request.user
    adjustment.status = "pending"


def _approve_adjustment(request, adjustment: AttendanceAdjustment):
    attendance = adjustment.attendance
    if adjustment.new_check_in:
        attendance.check_in_time = adjustment.new_check_in
    if adjustment.new_check_out:
        attendance.check_out_time = adjustment.new_check_out
    attendance.status = _derive_attendance_status(attendance.employee, attendance.check_in_time)
    attendance.remarks = adjustment.reason or attendance.remarks
    attendance.save(update_fields=["check_in_time", "check_out_time", "status", "remarks", "updated_at"])

    adjustment.status = "approved"
    adjustment.approved_by = request.user
    adjustment.save(update_fields=["status", "approved_by", "updated_at"])
    return {"message": "Attendance adjustment approved successfully."}


def _reject_adjustment(request, adjustment: AttendanceAdjustment):
    adjustment.status = "rejected"
    adjustment.approved_by = request.user
    adjustment.save(update_fields=["status", "approved_by", "updated_at"])
    return {"message": "Attendance adjustment rejected successfully."}


register_entity(
    EntityConfig(
        name="attendance_adjustment",
        url_path="attendance-adjustments",
        verbose_name="Attendance Adjustment",
        model=AttendanceAdjustment,
        form_class=AttendanceAdjustmentForm,
        datatable_view=AttendanceAdjustmentDataTableView,
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
                "name": "attendance_date",
                "label": "Attendance Date",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {
                "name": "new_check_in",
                "label": "New Check In",
                "type": "time",
                "required": False,
                "col": 6,
            },
            {
                "name": "new_check_out",
                "label": "New Check Out",
                "type": "time",
                "required": False,
                "col": 6,
            },
            {
                "name": "reason",
                "label": "Reason",
                "type": "textarea",
                "required": True,
                "col": 12,
            },
        ],
        post_save=_save_adjustment,
        row_actions={
            "approve": _approve_adjustment,
            "reject": _reject_adjustment,
        },
        action_state_field="status",
        hide_edit_on_values=["approved", "rejected"],
        hide_delete_on_values=["approved"],
        action_buttons=[
            {
                "action_name": "approve",
                "title": "Approve Adjustment",
                "label": "",
                "icon_class": "fas fa-check",
                "class_name": "btn-outline-success",
                "confirm_text": "Approve this attendance adjustment?",
                "success_message": "Attendance adjustment approved successfully.",
                "hide_on_values": ["approved", "rejected"],
            },
            {
                "action_name": "reject",
                "title": "Reject Adjustment",
                "label": "",
                "icon_class": "fas fa-times",
                "class_name": "btn-outline-danger",
                "confirm_text": "Reject this attendance adjustment?",
                "success_message": "Attendance adjustment rejected successfully.",
                "hide_on_values": ["approved", "rejected"],
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ATTENDANCE_ADJUSTMENT_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "attendance_date": timezone.localdate().isoformat(),
        },
        select_search_fields=[
            "attendance__employee__employee_id",
            "attendance__employee__user__first_name",
            "attendance__employee__user__last_name",
            "status",
            "reason",
        ],
    )
)
