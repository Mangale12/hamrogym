from core.datatables.views import BaseDataTableView
from nepanest.common.helpers.helper import encode_date_for_display, encode_datetime_for_display

from nepanest.modules.attendance.models import OvertimeRecord


OVERTIME_RECORD_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("overtime_date", lambda obj, request: encode_date_for_display(obj.overtime_date, request)),
    ("start_time", lambda obj: obj.start_time.strftime("%H:%M:%S") if obj.start_time else ""),
    ("end_time", lambda obj: obj.end_time.strftime("%H:%M:%S") if obj.end_time else ""),
    ("overtime_hours", "overtime_hours"),
    ("overtime_rate", "overtime_rate"),
    ("overtime_amount", "overtime_amount"),
    ("status", "status"),
    ("created_at", lambda obj, request: encode_datetime_for_display(obj.created_at, request)),
]


class OvertimeRecordDataTableView(BaseDataTableView):
    model = OvertimeRecord
    columns = OVERTIME_RECORD_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "employee__employee_id",
        "overtime_date",
        "status",
        "created_at",
    ]
