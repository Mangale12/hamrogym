from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display, encode_datetime_for_display

from ..models import (
    AttendancePayrollSummary,
    EmployeeSalaryAssignment,
    LeavePayrollImpact,
    PayrollAdjustment,
    PayrollRun,
    PayrollRunComponent,
    PayrollRunEmployee,
    SalaryComponent,
    SalaryStructure,
)


SALARY_COMPONENT_COLUMNS = [
    ("id", "id"),
    ("code", "code"),
    ("name", "name"),
    ("component_type", "component_type"),
    ("value_type", "value_type"),
    ("tax_treatment", "tax_treatment"),
    ("sequence", "sequence"),
    ("is_active", "is_active"),
]


SALARY_STRUCTURE_COLUMNS = [
    ("id", "id"),
    ("code", "code"),
    ("name", "name"),
    ("organization", lambda obj: str(obj.organization) if obj.organization else ""),
    ("branch", lambda obj: str(obj.branch) if obj.branch else ""),
    ("currency", lambda obj: str(obj.currency) if obj.currency else ""),
    ("effective_from", lambda obj, request: encode_date_for_display(obj.effective_from, request)),
    ("effective_to", lambda obj, request: encode_date_for_display(obj.effective_to, request)),
    ("is_active", "is_active"),
]


EMPLOYEE_SALARY_ASSIGNMENT_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("salary_structure", lambda obj: str(obj.salary_structure)),
    ("gross_salary", "gross_salary"),
    ("annual_ctc", "annual_ctc"),
    ("payment_frequency", "payment_frequency"),
    ("effective_from", lambda obj, request: encode_date_for_display(obj.effective_from, request)),
    ("effective_to", lambda obj, request: encode_date_for_display(obj.effective_to, request)),
    ("is_active", "is_active"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]

PAYROLL_RUN_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("payroll_year", "payroll_year"),
    ("payroll_month", "payroll_month"),
    ("period_start", lambda obj, request: encode_date_for_display(obj.period_start, request)),
    ("period_end", lambda obj, request: encode_date_for_display(obj.period_end, request)),
    ("employee_count", "employee_count"),
    ("total_gross", "total_gross"),
    ("total_deductions", "total_deductions"),
    ("total_net", "total_net"),
    ("status", "status"),
    ("processed_at", lambda obj, request: encode_datetime_for_display(obj.processed_at, request)),
]

PAYROLL_RUN_EMPLOYEE_COLUMNS = [
    ("id", "id"),
    ("payroll_run", lambda obj: str(obj.payroll_run)),
    ("employee", lambda obj: str(obj.employee)),
    ("salary_structure_name", "salary_structure_name"),
    ("gross_salary", "gross_salary"),
    ("gross_earnings", "gross_earnings"),
    ("total_deductions", "total_deductions"),
    ("net_salary", "net_salary"),
    ("status", "status"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]

PAYROLL_RUN_COMPONENT_COLUMNS = [
    ("id", "id"),
    ("payroll_run_employee", lambda obj: str(obj.payroll_run_employee)),
    ("salary_component", lambda obj: str(obj.salary_component)),
    ("source_type", "source_type"),
    ("sequence", "sequence"),
    ("quantity", "quantity"),
    ("rate", "rate"),
    ("amount", "amount"),
    ("created_at", lambda obj, request: encode_datetime_for_display(obj.created_at, request)),
]

ATTENDANCE_PAYROLL_SUMMARY_COLUMNS = [
    ("id", "id"),
    ("payroll_run", lambda obj: str(obj.payroll_run)),
    ("employee", lambda obj: str(obj.employee)),
    ("present_days", "present_days"),
    ("absent_days", "absent_days"),
    ("half_days", "half_days"),
    ("leave_days", "leave_days"),
    ("payable_days", "payable_days"),
    ("overtime_hours", "overtime_hours"),
    ("late_instances", "late_instances"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]

LEAVE_PAYROLL_IMPACT_COLUMNS = [
    ("id", "id"),
    ("payroll_run", lambda obj: str(obj.payroll_run)),
    ("employee", lambda obj: str(obj.employee)),
    ("leave_request", lambda obj: str(obj.leave_request) if obj.leave_request else ""),
    ("leave_type", lambda obj: str(obj.leave_type)),
    ("days", "days"),
    ("is_paid", "is_paid"),
    ("deduction_amount", "deduction_amount"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]

PAYROLL_ADJUSTMENT_COLUMNS = [
    ("id", "id"),
    ("payroll_run", lambda obj: str(obj.payroll_run)),
    ("employee", lambda obj: str(obj.employee)),
    ("salary_component", lambda obj: str(obj.salary_component) if obj.salary_component else ""),
    ("adjustment_type", "adjustment_type"),
    ("amount", "amount"),
    ("reason", "reason"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]


class SalaryComponentDataTableView(BaseDataTableView):
    model = SalaryComponent
    columns = SALARY_COMPONENT_COLUMNS
    searchable_columns = ["code", "name", "component_type", "value_type", "tax_treatment", "remarks"]
    orderable_columns = ["sequence", "code", "name", "component_type", "value_type", "is_active"]


class SalaryStructureDataTableView(BaseDataTableView):
    model = SalaryStructure
    columns = SALARY_STRUCTURE_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "organization__name",
        "branch__name",
        "currency__code",
        "currency__name",
        "description",
        "remarks",
    ]
    orderable_columns = ["code", "name", "effective_from", "effective_to", "is_active"]


class EmployeeSalaryAssignmentDataTableView(BaseDataTableView):
    model = EmployeeSalaryAssignment
    columns = EMPLOYEE_SALARY_ASSIGNMENT_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "salary_structure__code",
        "salary_structure__name",
        "payment_frequency",
        "remarks",
    ]
    orderable_columns = [
        "employee__employee_id",
        "salary_structure__name",
        "gross_salary",
        "payment_frequency",
        "effective_from",
        "is_active",
    ]


class PayrollRunDataTableView(BaseDataTableView):
    model = PayrollRun
    columns = PAYROLL_RUN_COLUMNS
    searchable_columns = [
        "name",
        "payroll_year",
        "payroll_month",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "payroll_year",
        "payroll_month",
        "period_start",
        "employee_count",
        "total_net",
        "status",
        "processed_at",
    ]


class PayrollRunEmployeeDataTableView(BaseDataTableView):
    model = PayrollRunEmployee
    columns = PAYROLL_RUN_EMPLOYEE_COLUMNS
    searchable_columns = [
        "payroll_run__name",
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "salary_structure_name",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "payroll_run__payroll_year",
        "payroll_run__payroll_month",
        "employee__employee_id",
        "gross_earnings",
        "total_deductions",
        "net_salary",
        "status",
        "updated_at",
    ]


class PayrollRunComponentDataTableView(BaseDataTableView):
    model = PayrollRunComponent
    columns = PAYROLL_RUN_COMPONENT_COLUMNS
    searchable_columns = [
        "payroll_run_employee__payroll_run__name",
        "payroll_run_employee__employee__employee_id",
        "salary_component__code",
        "salary_component__name",
        "source_type",
        "remarks",
    ]
    orderable_columns = [
        "payroll_run_employee__payroll_run__payroll_year",
        "payroll_run_employee__employee__employee_id",
        "sequence",
        "amount",
        "created_at",
    ]


class AttendancePayrollSummaryDataTableView(BaseDataTableView):
    model = AttendancePayrollSummary
    columns = ATTENDANCE_PAYROLL_SUMMARY_COLUMNS
    searchable_columns = [
        "payroll_run__name",
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "remarks",
    ]
    orderable_columns = [
        "payroll_run__payroll_year",
        "employee__employee_id",
        "payable_days",
        "overtime_hours",
        "late_instances",
        "updated_at",
    ]


class LeavePayrollImpactDataTableView(BaseDataTableView):
    model = LeavePayrollImpact
    columns = LEAVE_PAYROLL_IMPACT_COLUMNS
    searchable_columns = [
        "payroll_run__name",
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "leave_type__name",
        "remarks",
    ]
    orderable_columns = [
        "payroll_run__payroll_year",
        "employee__employee_id",
        "days",
        "deduction_amount",
        "updated_at",
    ]


class PayrollAdjustmentDataTableView(BaseDataTableView):
    model = PayrollAdjustment
    columns = PAYROLL_ADJUSTMENT_COLUMNS
    searchable_columns = [
        "payroll_run__name",
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "salary_component__code",
        "salary_component__name",
        "adjustment_type",
        "reason",
        "remarks",
    ]
    orderable_columns = [
        "payroll_run__payroll_year",
        "employee__employee_id",
        "adjustment_type",
        "amount",
        "updated_at",
    ]
