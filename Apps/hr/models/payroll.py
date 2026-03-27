from django.conf import settings
from django.db import models

from core.choices import (
    PAYMENT_FREQUENCY_CHOICES,
    PAYROLL_ADJUSTMENT_TYPE_CHOICES,
    PAYROLL_COMPONENT_SOURCE_TYPE_CHOICES,
    PAYROLL_COMPONENT_TYPE_CHOICES,
    PAYROLL_COMPONENT_VALUE_TYPE_CHOICES,
    PAYROLL_ROUNDING_RULE_CHOICES,
    PAYROLL_RUN_EMPLOYEE_STATUS_CHOICES,
    PAYROLL_RUN_STATUS_CHOICES,
    PAYROLL_TAX_TREATMENT_CHOICES,
)


class SalaryComponent(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100, unique=True)
    component_type = models.CharField(max_length=30, choices=PAYROLL_COMPONENT_TYPE_CHOICES)
    value_type = models.CharField(max_length=30, choices=PAYROLL_COMPONENT_VALUE_TYPE_CHOICES)
    formula_expression = models.TextField(blank=True)
    tax_treatment = models.CharField(
        max_length=30,
        choices=PAYROLL_TAX_TREATMENT_CHOICES,
        default="taxable",
    )
    affects_gross = models.BooleanField(default=True)
    affects_net = models.BooleanField(default=True)
    is_statutory = models.BooleanField(default=False)
    sequence = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sequence", "name"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class SalaryStructure(models.Model):
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "-effective_from"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "name", "effective_from"],
                name="unique_salary_structure_scope_name_effective_from",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class SalaryStructureComponent(models.Model):
    salary_structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.CASCADE,
        related_name="components",
    )
    salary_component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.PROTECT,
        related_name="structure_components",
    )
    percentage_of_component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="percentage_based_structure_components",
    )
    sequence = models.PositiveIntegerField(default=1)
    default_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    formula_expression = models.TextField(blank=True)
    min_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rounding_rule = models.CharField(
        max_length=20,
        choices=PAYROLL_ROUNDING_RULE_CHOICES,
        default="round_2",
    )
    is_mandatory = models.BooleanField(default=True)
    is_editable = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sequence", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["salary_structure", "salary_component"],
                name="unique_salary_structure_component",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.salary_structure} - {self.salary_component}"


class EmployeeSalaryAssignment(models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="salary_assignments",
        db_column="employee_id",
    )
    salary_structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.PROTECT,
        related_name="employee_assignments",
    )
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    annual_ctc = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCY_CHOICES,
        default="monthly",
    )
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="salary_assignments_approved",
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee__employee_id", "-effective_from", "-id"]

    def __str__(self) -> str:
        return f"{self.employee} - {self.salary_structure} ({self.effective_from})"


class EmployeeComponentOverride(models.Model):
    employee_salary_assignment = models.ForeignKey(
        EmployeeSalaryAssignment,
        on_delete=models.CASCADE,
        related_name="component_overrides",
    )
    salary_component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.PROTECT,
        related_name="employee_overrides",
    )
    override_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    override_formula = models.TextField(blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["salary_component__sequence", "salary_component__name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee_salary_assignment", "salary_component"],
                name="unique_employee_salary_override_component",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.employee_salary_assignment} - {self.salary_component}"


class PayrollRun(models.Model):
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=120)
    payroll_year = models.PositiveIntegerField()
    payroll_month = models.PositiveSmallIntegerField()
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=PAYROLL_RUN_STATUS_CHOICES,
        default="draft",
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_runs_processed",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_runs_approved",
    )
    employee_count = models.PositiveIntegerField(default=0)
    total_gross = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-payroll_year", "-payroll_month", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "payroll_year", "payroll_month"],
                name="unique_payroll_run_scope_period",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.payroll_year}-{self.payroll_month:02d})"


class PayrollRunEmployee(models.Model):
    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="employees",
    )
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.PROTECT,
        related_name="payroll_run_rows",
        db_column="employee_id",
    )
    employee_salary_assignment = models.ForeignKey(
        EmployeeSalaryAssignment,
        on_delete=models.PROTECT,
        related_name="payroll_run_rows",
    )
    salary_structure_name = models.CharField(max_length=120, blank=True)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_earnings = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    employer_contributions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    taxable_income = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    income_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=PAYROLL_RUN_EMPLOYEE_STATUS_CHOICES,
        default="pending",
    )
    calculation_summary = models.JSONField(default=dict, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee__employee_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["payroll_run", "employee"],
                name="unique_payroll_run_employee",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.payroll_run} - {self.employee}"


class PayrollRunComponent(models.Model):
    payroll_run_employee = models.ForeignKey(
        PayrollRunEmployee,
        on_delete=models.CASCADE,
        related_name="components",
    )
    salary_component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.PROTECT,
        related_name="payroll_run_components",
    )
    source_type = models.CharField(
        max_length=20,
        choices=PAYROLL_COMPONENT_SOURCE_TYPE_CHOICES,
        default="structure",
    )
    sequence = models.PositiveIntegerField(default=1)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    calculation_trace = models.JSONField(default=dict, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["payroll_run_employee", "salary_component"],
                name="unique_payroll_run_employee_component",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.payroll_run_employee} - {self.salary_component}"


class AttendancePayrollSummary(models.Model):
    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="attendance_summaries",
    )
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="attendance_payroll_summaries",
        db_column="employee_id",
    )
    present_days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    absent_days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    half_days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    leave_days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    payable_days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    late_instances = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee__employee_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["payroll_run", "employee"],
                name="unique_attendance_payroll_summary_run_employee",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.payroll_run} - {self.employee} attendance summary"


class LeavePayrollImpact(models.Model):
    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="leave_impacts",
    )
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="leave_payroll_impacts",
        db_column="employee_id",
    )
    leave_request = models.ForeignKey(
        "LeaveRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_impacts",
    )
    leave_type = models.ForeignKey(
        "LeaveType",
        on_delete=models.PROTECT,
        related_name="payroll_impacts",
    )
    days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=True)
    deduction_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee__employee_id", "leave_type__name", "id"]

    def __str__(self) -> str:
        return f"{self.payroll_run} - {self.employee} - {self.leave_type}"


class PayrollAdjustment(models.Model):
    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="adjustments",
    )
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="payroll_adjustments",
        db_column="employee_id",
    )
    salary_component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_adjustments",
    )
    adjustment_type = models.CharField(
        max_length=20,
        choices=PAYROLL_ADJUSTMENT_TYPE_CHOICES,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_adjustments_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee__employee_id", "-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.payroll_run} - {self.employee} - {self.adjustment_type}"
