from django.utils import timezone
from django.http import JsonResponse

from core.datatables.views import BaseDataTableView
from ..models import Attendance, Employee, Shift


def _today_attendance(employee: Employee):
    return getattr(employee, "_today_attendance", None)


def _employee_shift(employee: Employee):
    shift_value = (employee.shift or "").strip()
    if not shift_value:
        return None
    if hasattr(employee, "_resolved_shift"):
        return employee._resolved_shift
    shift = (
        Shift.objects.filter(code__iexact=shift_value).first()
        or Shift.objects.filter(name__iexact=shift_value).first()
    )
    employee._resolved_shift = shift
    return shift


def _attendance_action_state(employee: Employee):
    attendance = _today_attendance(employee)
    if not attendance or not attendance.check_in_time:
        return "can_check_in"
    if not attendance.check_out_time:
        return "can_check_out"
    return "completed"


def _attendance_action_label(employee: Employee):
    state = _attendance_action_state(employee)
    return {
        "can_check_in": "Check In",
        "can_check_out": "Check Out",
        "completed": "Completed",
    }.get(state, "")


ATTENDANCE_COLUMNS = [
    ("id", "id"),
    ("employee_id", "employee_id"),
    ("employee", lambda obj: obj.full_name or obj.user.username),
    ("shift", lambda obj: (obj.shift or "").strip()),
    (
        "date",
        lambda obj: timezone.localdate().isoformat(),
    ),
    (
        "check_in_time",
        lambda obj: obj._today_attendance.check_in_time.strftime("%H:%M:%S")
        if _today_attendance(obj) and _today_attendance(obj).check_in_time
        else "",
    ),
    (
        "check_out_time",
        lambda obj: obj._today_attendance.check_out_time.strftime("%H:%M:%S")
        if _today_attendance(obj) and _today_attendance(obj).check_out_time
        else "",
    ),
    ("status", lambda obj: _today_attendance(obj).status if _today_attendance(obj) else "pending"),
    (
        "remarks",
        lambda obj: (
            (_today_attendance(obj).remarks if _today_attendance(obj) else "")
        ),
    ),
    ("action_label", _attendance_action_label),
    ("action_state", _attendance_action_state),
]


class AttendanceDataTableView(BaseDataTableView):
    model = Employee
    columns = ATTENDANCE_COLUMNS

    def get_queryset(self):
        today = timezone.localdate()
        attendances = {
            attendance.employee_id: attendance
            for attendance in Attendance.objects.filter(date=today).select_related("employee")
        }
        employees = list(
            Employee.objects.select_related("user").filter(is_active=True).order_by("employee_id")
        )
        for employee in employees:
            employee._today_attendance = attendances.get(employee.id)
        return employees

    def filter_queryset(self, queryset, search_value):
        if not search_value:
            return queryset
        term = search_value.strip().lower()
        return [
            employee
            for employee in queryset
            if term in (employee.employee_id or "").lower()
            or term in (employee.full_name or "").lower()
            or term in (employee.user.username or "").lower()
            or term in ((employee.shift or "").lower())
        ]

    def order_queryset(self, queryset, order_index, order_dir):
        reverse = order_dir == "desc"
        key_name = self.orderable_columns[order_index] if order_index < len(self.orderable_columns) else "employee_id"

        def _sort_key(employee):
            if key_name == "user__first_name":
                return (employee.full_name or employee.user.username or "").lower()
            return (getattr(employee, key_name.split("__")[0], "") or "").lower()

        return sorted(queryset, key=_sort_key, reverse=reverse)

    def get(self, request, *args, **kwargs):
        draw = int(request.GET.get("draw", 1))
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))
        search_value = request.GET.get("search[value]", "")
        order_index = int(request.GET.get("order[0][column]", 0))
        order_dir = request.GET.get("order[0][dir]", "asc")
        first_column = request.GET.get("columns[0][data]", "")
        if first_column == "__sno__":
            order_index = max(order_index - 1, 0)

        queryset = self.get_queryset()
        total_records = len(queryset)
        queryset = self.filter_queryset(queryset, search_value)
        filtered_records = len(queryset)
        queryset = self.order_queryset(queryset, order_index, order_dir)
        page = queryset[start : start + length]
        data = [self.serialize_row(obj) for obj in page]

        return JsonResponse(
            {
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": filtered_records,
                "data": data,
            }
        )

    searchable_columns = [
        "employee_id",
        "user__first_name",
        "user__last_name",
        "shift",
    ]
    orderable_columns = [
        "employee_id",
        "user__first_name",
        "shift",
    ]
