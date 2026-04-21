from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display, encode_datetime_for_display

from ..models import AttendanceAdjustment


ATTENDANCE_ADJUSTMENT_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.attendance.employee)),
    (
        "attendance_date",
        lambda obj, request: encode_date_for_display(obj.attendance.date, request),
    ),
    ("current_check_in", lambda obj: obj.attendance.check_in_time.strftime("%H:%M:%S") if obj.attendance.check_in_time else ""),
    ("current_check_out", lambda obj: obj.attendance.check_out_time.strftime("%H:%M:%S") if obj.attendance.check_out_time else ""),
    ("new_check_in", lambda obj: obj.new_check_in.strftime("%H:%M:%S") if obj.new_check_in else ""),
    ("new_check_out", lambda obj: obj.new_check_out.strftime("%H:%M:%S") if obj.new_check_out else ""),
    ("status", "status"),
    ("reason", "reason"),
    ("requested_by", lambda obj: obj.requested_by.username if obj.requested_by else ""),
    ("approved_by", lambda obj: obj.approved_by.username if obj.approved_by else ""),
    ("created_at", lambda obj, request: encode_datetime_for_display(obj.created_at, request)),
]


class AttendanceAdjustmentDataTableView(BaseDataTableView):
    model = AttendanceAdjustment
    columns = ATTENDANCE_ADJUSTMENT_COLUMNS
    searchable_columns = [
        "attendance__employee__employee_id",
        "attendance__employee__user__first_name",
        "attendance__employee__user__last_name",
        "status",
        "reason",
        "requested_by__username",
        "approved_by__username",
    ]
    orderable_columns = [
        "attendance__employee__employee_id",
        "attendance__date",
        "status",
        "requested_by__username",
        "approved_by__username",
        "created_at",
    ]
