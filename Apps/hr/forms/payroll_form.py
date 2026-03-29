from django import forms

from ..models import (
    AttendancePayrollSummary,
    Employee,
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


def _employee_label(obj):
    return f"{obj.employee_id} - {obj.full_name or obj.user.username}"


class SalaryComponentForm(forms.ModelForm):
    class Meta:
        model = SalaryComponent
        fields = [
            "code",
            "name",
            "component_type",
            "value_type",
            "formula_expression",
            "tax_treatment",
            "affects_gross",
            "affects_net",
            "is_statutory",
            "sequence",
            "is_active",
            "remarks",
        ]


class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        fields = [
            "organization",
            "branch",
            "currency",
            "code",
            "name",
            "description",
            "effective_from",
            "effective_to",
            "is_active",
            "remarks",
        ]
        widgets = {
            "effective_from": forms.DateInput(attrs={"type": "date"}),
            "effective_to": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }


class EmployeeSalaryAssignmentForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = EmployeeSalaryAssignment
        fields = [
            "employee",
            "salary_structure",
            "gross_salary",
            "annual_ctc",
            "payment_frequency",
            "effective_from",
            "effective_to",
            "is_active",
            "remarks",
        ]
        widgets = {
            "effective_from": forms.DateInput(attrs={"type": "date"}),
            "effective_to": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = _employee_label


class PayrollRunForm(forms.ModelForm):
    class Meta:
        model = PayrollRun
        fields = [
            "organization",
            "branch",
            "currency",
            "name",
            "payroll_year",
            "payroll_month",
            "period_start",
            "period_end",
            "remarks",
        ]
        widgets = {
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }


class PayrollRunEmployeeForm(forms.ModelForm):
    class Meta:
        model = PayrollRunEmployee
        fields = [
            "payroll_run",
            "employee",
            "employee_salary_assignment",
            "salary_structure_name",
            "gross_salary",
            "gross_earnings",
            "total_deductions",
            "employer_contributions",
            "taxable_income",
            "income_tax",
            "net_salary",
            "status",
            "remarks",
        ]


class PayrollRunComponentForm(forms.ModelForm):
    class Meta:
        model = PayrollRunComponent
        fields = [
            "payroll_run_employee",
            "salary_component",
            "source_type",
            "sequence",
            "quantity",
            "rate",
            "amount",
            "remarks",
        ]


class AttendancePayrollSummaryForm(forms.ModelForm):
    class Meta:
        model = AttendancePayrollSummary
        fields = [
            "payroll_run",
            "employee",
            "present_days",
            "absent_days",
            "half_days",
            "leave_days",
            "payable_days",
            "overtime_hours",
            "late_instances",
            "remarks",
        ]


class LeavePayrollImpactForm(forms.ModelForm):
    class Meta:
        model = LeavePayrollImpact
        fields = [
            "payroll_run",
            "employee",
            "leave_request",
            "leave_type",
            "days",
            "is_paid",
            "deduction_amount",
            "remarks",
        ]


class PayrollAdjustmentForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = PayrollAdjustment
        fields = [
            "payroll_run",
            "employee",
            "salary_component",
            "adjustment_type",
            "amount",
            "reason",
            "remarks",
        ]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = _employee_label


class TaxSlabForm(forms.ModelForm):
    class Meta:
        model = TaxSlab
        fields = [
            "fiscal_year",
            "min_income",
            "max_income",
            "tax_rate",
            "rebate_amount",
            "is_active",
            "remarks",
        ]


class EmployeeTaxDeclarationForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = EmployeeTaxDeclaration
        fields = [
            "employee",
            "fiscal_year",
            "declared_amount",
            "investment_amount",
            "insurance_amount",
            "other_deductions",
            "remarks",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = _employee_label


class ProvidentFundForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = ProvidentFund
        fields = [
            "employee",
            "employee_percent",
            "employer_percent",
            "effective_from",
            "effective_to",
            "is_active",
            "remarks",
        ]
        widgets = {
            "effective_from": forms.DateInput(attrs={"type": "date"}),
            "effective_to": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = _employee_label


class SSFContributionForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = SSFContribution
        fields = [
            "employee",
            "employee_percent",
            "employer_percent",
            "effective_from",
            "effective_to",
            "is_active",
            "remarks",
        ]
        widgets = {
            "effective_from": forms.DateInput(attrs={"type": "date"}),
            "effective_to": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = _employee_label


class PayslipForm(forms.ModelForm):
    class Meta:
        model = Payslip
        fields = [
            "payroll_run_employee",
            "payslip_number",
            "generated_date",
            "file_path",
            "email_sent",
            "remarks",
        ]
        widgets = {
            "generated_date": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }


class PayrollApprovalForm(forms.ModelForm):
    class Meta:
        model = PayrollApproval
        fields = [
            "payroll_run",
            "approval_level",
            "approved_by",
            "status",
            "remarks",
            "approved_at",
        ]
        widgets = {
            "approved_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }


class PayrollLockForm(forms.ModelForm):
    class Meta:
        model = PayrollLock
        fields = [
            "payroll_run",
            "locked_by",
            "locked_at",
            "remarks",
        ]
        widgets = {
            "locked_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }


class PayrollLogForm(forms.ModelForm):
    class Meta:
        model = PayrollLog
        fields = [
            "payroll_run",
            "action",
            "performed_by",
            "old_data",
            "new_data",
        ]


class PayrollSettingForm(forms.ModelForm):
    class Meta:
        model = PayrollSetting
        fields = [
            "organization",
            "branch",
            "default_working_days",
            "overtime_calculation_method",
            "rounding_method",
            "adjustment_reference_type",
            "tax_deduction_component",
            "provident_fund_employee_component",
            "provident_fund_employer_component",
            "ssf_employee_component",
            "ssf_employer_component",
            "is_active",
            "remarks",
        ]
        widgets = {
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }


class ReportLayoutForm(forms.ModelForm):
    class Meta:
        model = ReportLayout
        fields = [
            "organization",
            "branch",
            "code",
            "name",
            "description",
            "html_wrapper",
            "css_content",
            "header_html",
            "footer_html",
            "is_active",
            "remarks",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "html_wrapper": forms.Textarea(attrs={"rows": 12}),
            "css_content": forms.Textarea(attrs={"rows": 8}),
            "header_html": forms.Textarea(attrs={"rows": 4}),
            "footer_html": forms.Textarea(attrs={"rows": 4}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }


class ReportTemplateForm(forms.ModelForm):
    class Meta:
        model = ReportTemplate
        fields = [
            "organization",
            "branch",
            "layout",
            "code",
            "name",
            "report_key",
            "description",
            "body_html",
            "css_content",
            "header_html",
            "footer_html",
            "sample_context",
            "is_default",
            "is_active",
            "remarks",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "body_html": forms.Textarea(attrs={"rows": 12}),
            "css_content": forms.Textarea(attrs={"rows": 8}),
            "header_html": forms.Textarea(attrs={"rows": 4}),
            "footer_html": forms.Textarea(attrs={"rows": 4}),
            "sample_context": forms.Textarea(attrs={"rows": 6}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }
