from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.attendance_data_table import AttendanceDataTableView, ATTENDANCE_COLUMNS
from ...forms.attendance_form import AttendanceDashboardForm
from ...models import Attendance, Employee, Shift


def _resolve_shift(employee: Employee):
    shift_value = (employee.shift or "").strip()
    if not shift_value:
        return None
    return (
        Shift.objects.filter(code__iexact=shift_value).first()
        or Shift.objects.filter(name__iexact=shift_value).first()
    )


def _today_attendance(employee: Employee):
    today = timezone.localdate()
    attendance, _ = Attendance.objects.get_or_create(
        employee=employee,
        date=today,
        defaults={"status": "pending"},
    )
    return attendance


def _derive_status(employee: Employee, check_in_time):
    if not check_in_time:
        return "pending"
    shift = _resolve_shift(employee)
    if not shift or not shift.grace_end_time:
        return "present"
    return "late" if check_in_time > shift.grace_end_time else "present"


def _check_in_employee(request, employee: Employee):
    attendance = _today_attendance(employee)
    if attendance.check_in_time:
        return {"message": "Employee is already checked in today."}

    now = timezone.localtime()
    attendance.check_in_time = now.time().replace(microsecond=0)
    attendance.status = _derive_status(employee, attendance.check_in_time)
    attendance.remarks = attendance.remarks or f"Checked in at {attendance.check_in_time.strftime('%H:%M:%S')}."
    attendance.save(update_fields=["check_in_time", "status", "remarks", "updated_at"])
    return {"message": "Check in recorded successfully."}


def _check_out_employee(request, employee: Employee):
    attendance = _today_attendance(employee)
    if not attendance.check_in_time:
        return {"message": "Employee must check in before check out."}
    if attendance.check_out_time:
        return {"message": "Employee is already checked out today."}

    now = timezone.localtime()
    attendance.check_out_time = now.time().replace(microsecond=0)
    attendance.save(update_fields=["check_out_time", "updated_at"])
    return {"message": "Check out recorded successfully."}


register_entity(
    EntityConfig(
        name="attendance",
        url_path="attendances",
        verbose_name="Attendance",
        model=Employee,
        form_class=AttendanceDashboardForm,
        datatable_view=AttendanceDataTableView,
        fields=[],
        row_actions={
            "check_in": _check_in_employee,
            "check_out": _check_out_employee,
        },
        action_state_field="action_state",
        hide_edit_on_values=["can_check_in", "can_check_out", "completed"],
        hide_delete_on_values=["can_check_in", "can_check_out", "completed"],
        action_buttons=[
            {
                "action_name": "check_in",
                "title": "Check In",
                "label": "Check In",
                "icon_class": "fas fa-sign-in-alt",
                "class_name": "btn-outline-success",
                "button_class": "entity-post-action-btn",
                "confirm_text": "Record check in for this employee?",
                "success_message": "Check in recorded successfully.",
                "hide_on_values": ["can_check_out", "completed"],
            },
            {
                "action_name": "check_out",
                "title": "Check Out",
                "label": "Check Out",
                "icon_class": "fas fa-sign-out-alt",
                "class_name": "btn-outline-warning",
                "button_class": "entity-post-action-btn",
                "confirm_text": "Record check out for this employee?",
                "success_message": "Check out recorded successfully.",
                "hide_on_values": ["can_check_in", "completed"],
            },
        ],
        datatable_columns=[
            {
                "name": key,
                "title": {
                    "employee_id": "Employee ID",
                    "check_in_time": "Check In",
                    "check_out_time": "Check Out",
                    "action_label": "Available Action",
                    "action_state": "Action State",
                }.get(key, key.replace("_", " ").title()),
                "visible": False if key == "action_state" else True,
            }
            for key, _accessor in ATTENDANCE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
        show_create=False,
        show_view=False,
        show_actions=True,
        select_search_fields=[
            "employee_id",
            "user__first_name",
            "user__last_name",
            "shift",
        ],
    )
)
