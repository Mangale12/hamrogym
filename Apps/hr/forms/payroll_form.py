from django import forms

from ..models import (
    AttendancePayrollSummary,
    Employee,
    EmployeeSalaryAssignment,
    LeavePayrollImpact,
    PayrollAdjustment,
    PayrollRun,
    PayrollRunComponent,
    PayrollRunEmployee,
    SalaryComponent,
    SalaryStructure,
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
