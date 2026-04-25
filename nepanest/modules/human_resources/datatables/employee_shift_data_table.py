from django.utils import timezone

from core.datatables.views import BaseDataTableView
from nepanest.common.helpers.helper import encode_datetime_for_display

from nepanest.modules.attendance.models import EmployeeShift


def _rotation_status(obj):
    now = timezone.localtime()
    if obj.effective_from and obj.effective_from > now:
        return "Upcoming"
    if obj.effective_to and obj.effective_to < now:
        return "Expired"
    return "Current"


EMPLOYEE_SHIFT_COLUMNS = [
    ("id", "id"),
    ("employee_id", lambda obj: obj.employee.employee_id),
    ("employee", lambda obj: obj.employee.full_name or obj.employee.user.username),
    ("shift", lambda obj: obj.shift.name or obj.shift.code or str(obj.shift)),
    ("rotation_status", _rotation_status),
    ("effective_from", lambda obj, request: encode_datetime_for_display(obj.effective_from, request) if obj.effective_from else ""),
    ("effective_to", lambda obj, request: encode_datetime_for_display(obj.effective_to, request) if obj.effective_to else ""),
    ("remarks", "remarks"),
]


class EmployeeShiftDataTableView(BaseDataTableView):
    model = EmployeeShift
    columns = EMPLOYEE_SHIFT_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "shift__name",
        "shift__code",
        "remarks",
    ]
    orderable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "shift__name",
        "effective_from",
        "effective_to",
    ]
