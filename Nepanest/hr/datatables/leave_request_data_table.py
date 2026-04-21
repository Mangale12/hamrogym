from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display, encode_datetime_for_display
from ..models import LeaveRequest


LEAVE_REQUEST_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("leave_type", lambda obj: str(obj.leave_type)),
    ("start_date", lambda obj, request: encode_date_for_display(obj.start_date, request)),
    ("end_date", lambda obj, request: encode_date_for_display(obj.end_date, request)),
    ("total_days", "total_days"),
    ("status", "status"),
    ("applied_at", lambda obj, request: encode_datetime_for_display(obj.applied_at, request)),
    ("approved_at", lambda obj, request: encode_datetime_for_display(obj.approved_at, request)),
]


class LeaveRequestDataTableView(BaseDataTableView):
    model = LeaveRequest
    columns = LEAVE_REQUEST_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "leave_type__name",
        "reason",
        "status",
    ]
    orderable_columns = [
        "id",
        "employee__employee_id",
        "leave_type__name",
        "start_date",
        "end_date",
        "total_days",
        "status",
        "applied_at",
    ]
