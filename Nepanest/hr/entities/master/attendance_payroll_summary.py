from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import AttendancePayrollSummaryDataTableView
from ...forms.payroll_form import AttendancePayrollSummaryForm
from ...models import AttendancePayrollSummary
from .payroll_shared import attendance_payroll_summary_columns


register_entity(
    EntityConfig(
        name="attendance_payroll_summary",
        url_path="attendance-payroll-summaries",
        verbose_name="Attendance Payroll Summary",
        model=AttendancePayrollSummary,
        form_class=AttendancePayrollSummaryForm,
        datatable_view=AttendancePayrollSummaryDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 6, "url_name": "payroll_run_select"},
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "present_days", "label": "Present Days", "type": "number", "required": False, "col": 3},
            {"name": "absent_days", "label": "Absent Days", "type": "number", "required": False, "col": 3},
            {"name": "half_days", "label": "Half Days", "type": "number", "required": False, "col": 3},
            {"name": "leave_days", "label": "Leave Days", "type": "number", "required": False, "col": 3},
            {"name": "payable_days", "label": "Payable Days", "type": "number", "required": False, "col": 4},
            {"name": "overtime_hours", "label": "Overtime Hours", "type": "number", "required": False, "col": 4},
            {"name": "late_instances", "label": "Late Instances", "type": "number", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=attendance_payroll_summary_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "payroll_run__name",
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
        ],
    )
)
