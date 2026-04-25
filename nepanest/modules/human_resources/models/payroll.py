from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.choices import (
    MONTH_CHOICES,
    PAYMENT_FREQUENCY_CHOICES,
    PAYROLL_ADJUSTMENT_TYPE_CHOICES,
    PAYROLL_APPROVAL_STATUS_CHOICES,
    PAYROLL_COMPONENT_SOURCE_TYPE_CHOICES,
    PAYROLL_COMPONENT_TYPE_CHOICES,
    PAYROLL_COMPONENT_VALUE_TYPE_CHOICES,
    PAYROLL_LOG_ACTION_CHOICES,
    PAYROLL_OVERTIME_CALCULATION_METHOD_CHOICES,
    PAYROLL_REFERENCE_TYPE_CHOICES,
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
        app_label = "hr"
        ordering = ["sequence", "name"]

    def clean(self):
        errors = {}
        if self.value_type == "formula" and not (self.formula_expression or "").strip():
            errors["formula_expression"] = "Formula expression is required when value type is formula."
        if self.value_type != "formula" and (self.formula_expression or "").strip():
            errors["formula_expression"] = "Formula expression should only be set for formula-based components."
        if self.component_type == "deduction" and self.affects_gross:
            errors["affects_gross"] = "Deduction components should not affect gross salary."
        if errors:
            raise ValidationError(errors)

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
        app_label = "hr"
        ordering = ["name", "-effective_from"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "name", "effective_from"],
                name="unique_salary_structure_scope_name_effective_from",
            ),
        ]

    def clean(self):
        errors = {}
        if self.branch_id and not self.organization_id:
            errors["organization"] = "Organization is required when branch is selected."
        if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
            errors["effective_to"] = "Effective to date cannot be earlier than effective from date."
        if errors:
            raise ValidationError(errors)

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
        app_label = "hr"
        ordering = ["sequence", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["salary_structure", "salary_component"],
                name="unique_salary_structure_component",
            ),
        ]

    def clean(self):
        errors = {}
        formula_expression = (self.formula_expression or "").strip()
        if self.percentage_of_component_id and self.percentage_of_component_id == self.salary_component_id:
            errors["percentage_of_component"] = "Percentage base component cannot be the same as salary component."
        if self.min_value is not None and self.max_value is not None and self.min_value > self.max_value:
            errors["max_value"] = "Max value cannot be less than min value."
        if self.default_value is not None and self.default_value < 0:
            errors["default_value"] = "Default value cannot be negative."
        if self.min_value is not None and self.min_value < 0:
            errors["min_value"] = "Min value cannot be negative."
        if self.max_value is not None and self.max_value < 0:
            errors["max_value"] = "Max value cannot be negative."
        if self.percentage_of_component_id and self.default_value is None:
            errors["default_value"] = "Percentage value is required when percentage base component is selected."
        if formula_expression and self.default_value is not None:
            errors["default_value"] = "Default value should be empty when formula expression is used."
        if formula_expression and self.percentage_of_component_id:
            errors["percentage_of_component"] = "Percentage base component should be empty when formula expression is used."
        if errors:
            raise ValidationError(errors)

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
        app_label = "hr"
        ordering = ["employee__employee_id", "-effective_from", "-id"]

    def clean(self):
        errors = {}
        if self.gross_salary is not None and self.gross_salary <= 0:
            errors["gross_salary"] = "Gross salary must be greater than zero."
        if self.annual_ctc is not None and self.annual_ctc < 0:
            errors["annual_ctc"] = "Annual CTC cannot be negative."
        if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
            errors["effective_to"] = "Effective to date cannot be earlier than effective from date."
        if errors:
            raise ValidationError(errors)

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
        app_label = "hr"
        ordering = ["salary_component__sequence", "salary_component__name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee_salary_assignment", "salary_component"],
                name="unique_employee_salary_override_component",
            ),
        ]

    def clean(self):
        errors = {}
        override_formula = (self.override_formula or "").strip()
        if self.override_value is None and not override_formula:
            errors["override_value"] = "Set either an override value or override formula."
        if self.override_value is not None and override_formula:
            errors["override_formula"] = "Use either override value or override formula, not both."
        if self.override_value is not None and self.override_value < 0:
            errors["override_value"] = "Override value cannot be negative."
        if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
            errors["effective_to"] = "Effective to date cannot be earlier than effective from date."
        if errors:
            raise ValidationError(errors)

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
    fiscal_year = models.ForeignKey(
        "core.FiscalYear",
        on_delete=models.PROTECT,
        related_name="payroll_runs",
    )
    name = models.CharField(max_length=120)
    payroll_year = models.PositiveIntegerField()
    payroll_month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
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
        app_label = "hr"
        ordering = ["-payroll_year", "-payroll_month", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "fiscal_year", "payroll_month"],
                name="unique_payroll_run_scope_fiscal_year_month",
            ),
        ]

    def clean(self):
        errors = {}
        if self.fiscal_year_id and self.period_start and self.period_end:
            if self.period_start < self.fiscal_year.start_date or self.period_end > self.fiscal_year.end_date:
                errors["period_end"] = "Payroll period must fall within the selected fiscal year."
        if self.period_start:
            self.payroll_year = self.period_start.year
        if self.branch_id and not self.organization_id:
            errors["organization"] = "Organization is required when branch is selected."
        if self.payroll_month and not 1 <= self.payroll_month <= 12:
            errors["payroll_month"] = "Payroll month must be between 1 and 12."
        if self.period_end and self.period_start and self.period_end < self.period_start:
            errors["period_end"] = "Period end cannot be earlier than period start."
        if errors:
            raise ValidationError(errors)

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
        app_label = "hr"
        ordering = ["employee__employee_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["payroll_run", "employee"],
                name="unique_payroll_run_employee",
            ),
        ]

    def __str__(self) -> str:
        try:
            payroll_run = self.payroll_run
        except PayrollRun.DoesNotExist:
            payroll_run = f"Payroll Run #{self.payroll_run_id or 'missing'}"

        try:
            employee = self.employee
        except Exception:
            employee = f"Employee #{self.employee_id or 'missing'}"

        return f"{payroll_run} - {employee}"


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
        app_label = "hr"
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
        app_label = "hr"
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
        app_label = "hr"
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
        app_label = "hr"
        ordering = ["employee__employee_id", "-created_at", "-id"]

    def clean(self):
        errors = {}
        if self.amount is not None and self.amount <= 0:
            errors["amount"] = "Adjustment amount must be greater than zero."
        if self.payroll_run_id and self.employee_id:
            has_employee = self.payroll_run.employees.filter(employee_id=self.employee_id).exists()
            if self.payroll_run.status in {"processed", "reviewed", "approved", "locked"} and not has_employee:
                errors["employee"] = "Selected employee is not part of this payroll run."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.payroll_run} - {self.employee} - {self.adjustment_type}"


class TaxSlab(models.Model):
    fiscal_year = models.ForeignKey(
        "core.FiscalYear",
        on_delete=models.PROTECT,
        related_name="payroll_tax_slabs",
    )
    min_income = models.DecimalField(max_digits=14, decimal_places=2)
    max_income = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    rebate_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["fiscal_year__start_date", "min_income", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["fiscal_year", "min_income"],
                name="unique_tax_slab_fiscal_year_min_income",
            ),
        ]

    def clean(self):
        errors = {}
        if self.min_income is not None and self.min_income < 0:
            errors["min_income"] = "Min income cannot be negative."
        if self.max_income is not None and self.max_income < 0:
            errors["max_income"] = "Max income cannot be negative."
        if self.max_income is not None and self.min_income is not None and self.max_income <= self.min_income:
            errors["max_income"] = "Max income must be greater than min income."
        if self.tax_rate is not None and (self.tax_rate < 0 or self.tax_rate > 100):
            errors["tax_rate"] = "Tax rate must be between 0 and 100."
        if self.rebate_amount is not None and self.rebate_amount < 0:
            errors["rebate_amount"] = "Rebate amount cannot be negative."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        upper = self.max_income if self.max_income is not None else "Above"
        return f"{self.fiscal_year} - {self.min_income} to {upper}"


class EmployeeTaxDeclaration(models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="tax_declarations",
        db_column="employee_id",
    )
    fiscal_year = models.ForeignKey(
        "core.FiscalYear",
        on_delete=models.PROTECT,
        related_name="employee_tax_declarations",
    )
    declared_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    investment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["employee__employee_id", "-fiscal_year__start_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "fiscal_year"],
                name="unique_employee_tax_declaration_fiscal_year",
            ),
        ]

    def clean(self):
        errors = {}
        for field_name in [
            "declared_amount",
            "investment_amount",
            "insurance_amount",
            "other_deductions",
        ]:
            value = getattr(self, field_name)
            if value is not None and value < 0:
                errors[field_name] = "Amount cannot be negative."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.employee} - {self.fiscal_year}"


class ProvidentFund(models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="provident_funds",
        db_column="employee_id",
    )
    employee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    employer_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["employee__employee_id", "-effective_from", "-id"]

    def clean(self):
        errors = {}
        if self.employee_percent is not None and not 0 <= self.employee_percent <= 100:
            errors["employee_percent"] = "Employee percent must be between 0 and 100."
        if self.employer_percent is not None and not 0 <= self.employer_percent <= 100:
            errors["employer_percent"] = "Employer percent must be between 0 and 100."
        if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
            errors["effective_to"] = "Effective to date cannot be earlier than effective from date."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.employee} PF ({self.employee_percent}%/{self.employer_percent}%)"


class SSFContribution(models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="ssf_contributions",
        db_column="employee_id",
    )
    employee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    employer_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["employee__employee_id", "-effective_from", "-id"]

    def clean(self):
        errors = {}
        if self.employee_percent is not None and not 0 <= self.employee_percent <= 100:
            errors["employee_percent"] = "Employee percent must be between 0 and 100."
        if self.employer_percent is not None and not 0 <= self.employer_percent <= 100:
            errors["employer_percent"] = "Employer percent must be between 0 and 100."
        if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
            errors["effective_to"] = "Effective to date cannot be earlier than effective from date."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.employee} SSF ({self.employee_percent}%/{self.employer_percent}%)"


class Payslip(models.Model):
    payroll_run_employee = models.OneToOneField(
        PayrollRunEmployee,
        on_delete=models.CASCADE,
        related_name="payslip",
    )
    payslip_number = models.CharField(max_length=50, unique=True)
    generated_date = models.DateField()
    file_path = models.CharField(max_length=255, blank=True)
    email_sent = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["-generated_date", "-id"]

    def clean(self):
        errors = {}
        if self.payroll_run_employee_id and self.generated_date:
            period_start = self.payroll_run_employee.payroll_run.period_start
            if self.generated_date < period_start:
                errors["generated_date"] = "Generated date cannot be earlier than the payroll period start."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.payslip_number


class PayrollApproval(models.Model):
    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="approvals",
    )
    approval_level = models.PositiveIntegerField(default=1)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_approvals",
    )
    status = models.CharField(
        max_length=20,
        choices=PAYROLL_APPROVAL_STATUS_CHOICES,
        default="pending",
    )
    remarks = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["payroll_run__payroll_year", "payroll_run__payroll_month", "approval_level", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["payroll_run", "approval_level"],
                name="unique_payroll_approval_level_per_run",
            ),
        ]

    def clean(self):
        errors = {}
        if self.approval_level is not None and self.approval_level < 1:
            errors["approval_level"] = "Approval level must be at least 1."
        if self.status == "approved" and not self.approved_by_id:
            errors["approved_by"] = "Approved by is required when status is approved."
        if self.status == "approved" and not self.approved_at:
            errors["approved_at"] = "Approved at is required when status is approved."
        if self.status == "pending" and self.approved_at:
            errors["approved_at"] = "Approved at should be empty while approval is pending."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.payroll_run} - Level {self.approval_level}"


class PayrollLock(models.Model):
    payroll_run = models.OneToOneField(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="lock_record",
    )
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_locks",
    )
    locked_at = models.DateTimeField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"
        ordering = ["-locked_at", "-id"]

    def clean(self):
        errors = {}
        if self.payroll_run_id and self.payroll_run.status != "approved":
            errors["payroll_run"] = "Only approved payroll runs can be locked."
        if not self.locked_by_id:
            errors["locked_by"] = "Locked by is required."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.payroll_run} locked"


class PayrollLog(models.Model):
    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    action = models.CharField(max_length=20, choices=PAYROLL_LOG_ACTION_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_logs",
    )
    old_data = models.JSONField(blank=True, null=True)
    new_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.payroll_run} - {self.action}"


class PayrollSetting(models.Model):
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_settings",
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_settings",
    )
    default_working_days = models.PositiveSmallIntegerField(default=30)
    overtime_calculation_method = models.CharField(
        max_length=30,
        choices=PAYROLL_OVERTIME_CALCULATION_METHOD_CHOICES,
        default="hourly_rate",
    )
    rounding_method = models.CharField(
        max_length=20,
        choices=PAYROLL_ROUNDING_RULE_CHOICES,
        default="round_2",
    )
    adjustment_reference_type = models.CharField(
        max_length=20,
        choices=PAYROLL_REFERENCE_TYPE_CHOICES,
        default="manual",
    )
    tax_deduction_component = models.ForeignKey(
        "SalaryComponent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_settings_tax_component",
    )
    provident_fund_employee_component = models.ForeignKey(
        "SalaryComponent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_settings_pf_employee_component",
    )
    provident_fund_employer_component = models.ForeignKey(
        "SalaryComponent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_settings_pf_employer_component",
    )
    ssf_employee_component = models.ForeignKey(
        "SalaryComponent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_settings_ssf_employee_component",
    )
    ssf_employer_component = models.ForeignKey(
        "SalaryComponent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_settings_ssf_employer_component",
    )
    overtime_earning_component = models.ForeignKey(
        "SalaryComponent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_settings_overtime_component",
    )
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["organization__name", "branch__name", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch"],
                name="unique_payroll_setting_scope",
            ),
        ]

    def clean(self):
        errors = {}
        if self.branch_id and not self.organization_id:
            errors["organization"] = "Organization is required when branch is selected."

        component_rules = [
            ("tax_deduction_component", {"deduction"}),
            ("provident_fund_employee_component", {"deduction"}),
            ("provident_fund_employer_component", {"employer_contribution"}),
            ("ssf_employee_component", {"deduction"}),
            ("ssf_employer_component", {"employer_contribution"}),
            ("overtime_earning_component", {"earning"}),
        ]
        for field_name, allowed_types in component_rules:
            component = getattr(self, field_name)
            if component and component.component_type not in allowed_types:
                errors[field_name] = f"Selected component must be one of: {', '.join(sorted(allowed_types))}."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        scope = self.branch or self.organization or "Global"
        return f"{scope} Payroll Settings"


class ReportLayout(models.Model):
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="report_layouts",
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="report_layouts",
    )
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    html_wrapper = models.TextField(
        help_text="Shared HTML shell. Use {{ report_styles }}, {{ report_header }}, {{ report_body }}, and {{ report_footer }} placeholders.",
    )
    css_content = models.TextField(blank=True)
    header_html = models.TextField(blank=True)
    footer_html = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["name", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "name"],
                name="unique_report_layout_scope_name",
            ),
        ]

    def clean(self):
        errors = {}
        if self.branch_id and not self.organization_id:
            errors["organization"] = "Organization is required when branch is selected."
        if "{{ report_body }}" not in (self.html_wrapper or ""):
            errors["html_wrapper"] = "HTML wrapper must include {{ report_body }} placeholder."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class ReportTemplate(models.Model):
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="report_templates",
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="report_templates",
    )
    layout = models.ForeignKey(
        ReportLayout,
        on_delete=models.PROTECT,
        related_name="report_templates",
    )
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    report_key = models.CharField(
        max_length=50,
        help_text="Logical report identifier like payslip, salary_register, attendance_summary, or member_invoice.",
    )
    description = models.TextField(blank=True)
    body_html = models.TextField(
        help_text="Template body HTML. You can use Django-style variables such as {{ employee_name }} or {{ company_name }}.",
    )
    css_content = models.TextField(blank=True)
    header_html = models.TextField(blank=True)
    footer_html = models.TextField(blank=True)
    sample_context = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["report_key", "name", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "report_key", "name"],
                name="unique_report_template_scope_key_name",
            ),
        ]

    def clean(self):
        errors = {}
        if self.branch_id and not self.organization_id:
            errors["organization"] = "Organization is required when branch is selected."
        if self.layout_id and self.branch_id and self.layout.branch_id and self.layout.branch_id != self.branch_id:
            errors["layout"] = "Layout branch must match the report template branch."
        if self.layout_id and self.organization_id and self.layout.organization_id and self.layout.organization_id != self.organization_id:
            errors["layout"] = "Layout organization must match the report template organization."
        if not (self.body_html or "").strip():
            errors["body_html"] = "Body HTML is required."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
