from Apps.hr.models.employee import Employee
from core.datatables.views import BaseDataTableView
from ..models import Attendance


ATTENDANCE_COLUMNS = [
    ("id", "id"),
    ('employee', 'Employee'),
    ('date', 'Date'),
    ('check_in_time', 'Check In Time'),
    ('check_out_time', 'Check Out Time'),
    ('status', 'Status'),
    ('remarks', 'Remarks'),
    ('created_at', 'Created At'),
    ('updated_at', 'Updated At'),
]


class AttendanceDataTableView(BaseDataTableView):
    model = Employee
    columns = ATTENDANCE_COLUMNS
    searchable_columns = [
        'employee__name',
        'date',
        'check_in_time',
        'check_out_time',
        'status',
        'remarks',
        'created_at',
        'updated_at',
    ]
    orderable_columns = [
        'employee__name',
        'date',
        'check_in_time',
        'check_out_time',
        'status',
        'remarks',
        'created_at',
        'updated_at',
    ]
