from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display, encode_datetime_for_display

from ..models import (
    AttendancePayrollSummary,
    EmployeeSalaryAssignment,
    EmployeeTaxDeclaration,
    LeavePayrollImpact,
    PayrollAdjustment,
    PayrollApproval,
    PayrollLock,
    PayrollLog,
    PayrollRun,
    PayrollRunComponent,
    PayrollRunEmployee,
    PayrollSetting,
    Payslip,
    ProvidentFund,
    ReportLayout,
    ReportTemplate,
    SalaryComponent,
    SalaryStructure,
    SSFContribution,
    TaxSlab,
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
    ("fiscal_year", lambda obj: str(obj.fiscal_year)),
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

TAX_SLAB_COLUMNS = [
    ("id", "id"),
    ("fiscal_year", lambda obj: str(obj.fiscal_year)),
    ("min_income", "min_income"),
    ("max_income", "max_income"),
    ("tax_rate", "tax_rate"),
    ("rebate_amount", "rebate_amount"),
    ("is_active", "is_active"),
]

EMPLOYEE_TAX_DECLARATION_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("fiscal_year", lambda obj: str(obj.fiscal_year)),
    ("declared_amount", "declared_amount"),
    ("investment_amount", "investment_amount"),
    ("insurance_amount", "insurance_amount"),
    ("other_deductions", "other_deductions"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]

PROVIDENT_FUND_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("employee_percent", "employee_percent"),
    ("employer_percent", "employer_percent"),
    ("effective_from", lambda obj, request: encode_date_for_display(obj.effective_from, request)),
    ("effective_to", lambda obj, request: encode_date_for_display(obj.effective_to, request)),
    ("is_active", "is_active"),
]

SSF_CONTRIBUTION_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("employee_percent", "employee_percent"),
    ("employer_percent", "employer_percent"),
    ("effective_from", lambda obj, request: encode_date_for_display(obj.effective_from, request)),
    ("effective_to", lambda obj, request: encode_date_for_display(obj.effective_to, request)),
    ("is_active", "is_active"),
]

PAYSLIP_COLUMNS = [
    ("id", "id"),
    ("payroll_run_employee", lambda obj: str(obj.payroll_run_employee)),
    ("payslip_number", "payslip_number"),
    ("generated_date", lambda obj, request: encode_date_for_display(obj.generated_date, request)),
    ("file_path", "file_path"),
    ("email_sent", "email_sent"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]

PAYROLL_APPROVAL_COLUMNS = [
    ("id", "id"),
    ("payroll_run", lambda obj: str(obj.payroll_run)),
    ("approval_level", "approval_level"),
    ("approved_by", lambda obj: str(obj.approved_by) if obj.approved_by else ""),
    ("status", "status"),
    ("approved_at", lambda obj, request: encode_datetime_for_display(obj.approved_at, request)),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]

PAYROLL_LOCK_COLUMNS = [
    ("id", "id"),
    ("payroll_run", lambda obj: str(obj.payroll_run)),
    ("locked_by", lambda obj: str(obj.locked_by) if obj.locked_by else ""),
    ("locked_at", lambda obj, request: encode_datetime_for_display(obj.locked_at, request)),
    ("created_at", lambda obj, request: encode_datetime_for_display(obj.created_at, request)),
]

PAYROLL_LOG_COLUMNS = [
    ("id", "id"),
    ("payroll_run", lambda obj: str(obj.payroll_run)),
    ("action", "action"),
    ("performed_by", lambda obj: str(obj.performed_by) if obj.performed_by else ""),
    ("created_at", lambda obj, request: encode_datetime_for_display(obj.created_at, request)),
]

PAYROLL_SETTING_COLUMNS = [
    ("id", "id"),
    ("organization", lambda obj: str(obj.organization) if obj.organization else ""),
    ("branch", lambda obj: str(obj.branch) if obj.branch else ""),
    ("default_working_days", "default_working_days"),
    ("overtime_calculation_method", "overtime_calculation_method"),
    ("rounding_method", "rounding_method"),
    ("tax_deduction_component", lambda obj: str(obj.tax_deduction_component) if obj.tax_deduction_component else ""),
    ("overtime_earning_component", lambda obj: str(obj.overtime_earning_component) if obj.overtime_earning_component else ""),
    ("is_active", "is_active"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]

REPORT_LAYOUT_COLUMNS = [
    ("id", "id"),
    ("organization", lambda obj: str(obj.organization) if obj.organization else ""),
    ("branch", lambda obj: str(obj.branch) if obj.branch else ""),
    ("code", "code"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]

REPORT_TEMPLATE_COLUMNS = [
    ("id", "id"),
    ("organization", lambda obj: str(obj.organization) if obj.organization else ""),
    ("branch", lambda obj: str(obj.branch) if obj.branch else ""),
    ("layout", lambda obj: str(obj.layout)),
    ("code", "code"),
    ("name", "name"),
    ("report_key", "report_key"),
    ("is_default", "is_default"),
    ("is_active", "is_active"),
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
        "fiscal_year__name",
        "payroll_month",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "fiscal_year__start_date",
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


class TaxSlabDataTableView(BaseDataTableView):
    model = TaxSlab
    columns = TAX_SLAB_COLUMNS
    searchable_columns = ["fiscal_year__name", "remarks"]
    orderable_columns = ["fiscal_year__start_date", "min_income", "tax_rate", "is_active"]


class EmployeeTaxDeclarationDataTableView(BaseDataTableView):
    model = EmployeeTaxDeclaration
    columns = EMPLOYEE_TAX_DECLARATION_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "fiscal_year__name",
        "remarks",
    ]
    orderable_columns = ["employee__employee_id", "fiscal_year__start_date", "declared_amount", "updated_at"]


class ProvidentFundDataTableView(BaseDataTableView):
    model = ProvidentFund
    columns = PROVIDENT_FUND_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "remarks",
    ]
    orderable_columns = ["employee__employee_id", "effective_from", "employee_percent", "employer_percent", "is_active"]


class SSFContributionDataTableView(BaseDataTableView):
    model = SSFContribution
    columns = SSF_CONTRIBUTION_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "remarks",
    ]
    orderable_columns = ["employee__employee_id", "effective_from", "employee_percent", "employer_percent", "is_active"]


class PayslipDataTableView(BaseDataTableView):
    model = Payslip
    columns = PAYSLIP_COLUMNS
    searchable_columns = [
        "payroll_run_employee__payroll_run__name",
        "payroll_run_employee__employee__employee_id",
        "payslip_number",
        "file_path",
        "remarks",
    ]
    orderable_columns = ["generated_date", "payslip_number", "email_sent", "updated_at"]


class PayrollApprovalDataTableView(BaseDataTableView):
    model = PayrollApproval
    columns = PAYROLL_APPROVAL_COLUMNS
    searchable_columns = ["payroll_run__name", "approved_by__username", "status", "remarks"]
    orderable_columns = ["payroll_run__payroll_year", "approval_level", "status", "approved_at", "updated_at"]


class PayrollLockDataTableView(BaseDataTableView):
    model = PayrollLock
    columns = PAYROLL_LOCK_COLUMNS
    searchable_columns = ["payroll_run__name", "locked_by__username", "remarks"]
    orderable_columns = ["locked_at", "created_at"]


class PayrollLogDataTableView(BaseDataTableView):
    model = PayrollLog
    columns = PAYROLL_LOG_COLUMNS
    searchable_columns = ["payroll_run__name", "action", "performed_by__username"]
    orderable_columns = ["created_at", "action"]


class PayrollSettingDataTableView(BaseDataTableView):
    model = PayrollSetting
    columns = PAYROLL_SETTING_COLUMNS
    searchable_columns = [
        "organization__name",
        "branch__name",
        "overtime_calculation_method",
        "tax_deduction_component__code",
        "tax_deduction_component__name",
        "overtime_earning_component__code",
        "overtime_earning_component__name",
        "remarks",
    ]
    orderable_columns = ["organization__name", "branch__name", "default_working_days", "is_active", "updated_at"]


class ReportLayoutDataTableView(BaseDataTableView):
    model = ReportLayout
    columns = REPORT_LAYOUT_COLUMNS
    searchable_columns = [
        "organization__name",
        "branch__name",
        "code",
        "name",
        "description",
        "remarks",
    ]
    orderable_columns = ["organization__name", "branch__name", "code", "name", "is_active", "updated_at"]


class ReportTemplateDataTableView(BaseDataTableView):
    model = ReportTemplate
    columns = REPORT_TEMPLATE_COLUMNS
    searchable_columns = [
        "organization__name",
        "branch__name",
        "layout__code",
        "layout__name",
        "code",
        "name",
        "report_key",
        "description",
        "remarks",
    ]
    orderable_columns = [
        "organization__name",
        "branch__name",
        "report_key",
        "code",
        "name",
        "is_default",
        "is_active",
        "updated_at",
    ]
