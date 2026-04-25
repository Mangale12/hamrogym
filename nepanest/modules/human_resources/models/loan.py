from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.choices import (
    APPROVAL_STATUS_CHOICES,
    INTEREST_TYPE_CHOICES,
    LOAN_ACCOUNT_STATUS_CHOICES,
    LOAN_ADJUSTMENT_TYPE_CHOICES,
    LOAN_APPLICATION_STATUS_CHOICES,
    LOAN_INSTALLMENT_STATUS_CHOICES,
    LOAN_LEDGER_TRANSACTION_TYPE_CHOICES,
    PAYMENT_METHOD_CHOICES,
)


class LoanApplication(models.Model):
    employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="loan_applications", db_column="employee_id")
    loan_type = models.ForeignKey("LoanType", on_delete=models.PROTECT, related_name="applications")
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
    requested_tenure = models.PositiveIntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=LOAN_APPLICATION_STATUS_CHOICES, default="draft")
    applied_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="loan_applications_approved")
    approved_date = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="loan_applications_rejected")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["-applied_date", "-id"]

    def clean(self):
        if self.requested_amount <= 0:
            raise ValidationError({"requested_amount": "Requested amount must be greater than zero."})
        if self.requested_tenure <= 0:
            raise ValidationError({"requested_tenure": "Requested tenure must be greater than zero."})
        if self.loan_type_id:
            if self.requested_amount > self.loan_type.max_loan_amount:
                raise ValidationError({"requested_amount": "Requested amount exceeds the loan type maximum."})
            if self.requested_tenure < self.loan_type.min_tenure_months:
                raise ValidationError({"requested_tenure": "Requested tenure is below the loan type minimum."})
            if self.requested_tenure > self.loan_type.max_tenure_months:
                raise ValidationError({"requested_tenure": "Requested tenure exceeds the loan type maximum."})

    def __str__(self) -> str:
        return f"{self.employee} - {self.loan_type} ({self.requested_amount})"


class LoanApprovalHistory(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name="approvals")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loan_approval_actions")
    level = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="pending")
    remarks = models.TextField(blank=True)
    action_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"
        ordering = ["level", "id"]
        constraints = [
            models.UniqueConstraint(fields=["loan_application", "level"], name="unique_loan_approval_level"),
            models.UniqueConstraint(fields=["loan_application", "approved_by", "level"], name="unique_loan_approval_approver_level"),
        ]


class LoanAccount(models.Model):
    loan_application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE, related_name="loan_account")
    employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="loan_accounts", db_column="employee_id")
    loan_type = models.ForeignKey("LoanType", on_delete=models.PROTECT, related_name="loan_accounts")
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPE_CHOICES, default="flat")
    tenure_months = models.PositiveIntegerField()
    emi_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    disbursement_date = models.DateField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=LOAN_ACCOUNT_STATUS_CHOICES, default="active")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["-created_at", "-id"]


class LoanDisbursement(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE, related_name="disbursements")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    disbursed_date = models.DateField()
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="bank")
    reference_no = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"
        ordering = ["-disbursed_date", "-id"]


class LoanInstallment(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE, related_name="installments")
    installment_no = models.PositiveIntegerField()
    due_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=LOAN_INSTALLMENT_STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["loan_account", "installment_no"]
        constraints = [
            models.UniqueConstraint(fields=["loan_account", "installment_no"], name="unique_loan_installment_number"),
        ]


class LoanRepayment(models.Model):
    loan_installment = models.ForeignKey(LoanInstallment, on_delete=models.CASCADE, related_name="repayments")
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="bank")
    reference_no = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"
        ordering = ["-payment_date", "-id"]


class LoanPayrollDeduction(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE, related_name="payroll_deductions")
    payroll_run = models.ForeignKey("PayrollRun", on_delete=models.CASCADE, related_name="loan_deductions")
    employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="loan_payroll_deductions", db_column="employee_id")
    installment = models.ForeignKey(LoanInstallment, on_delete=models.CASCADE, related_name="payroll_deductions")
    deducted_amount = models.DecimalField(max_digits=12, decimal_places=2)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"


class LoanAdjustment(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE, related_name="adjustments")
    adjustment_type = models.CharField(max_length=20, choices=LOAN_ADJUSTMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"


class LoanPenalty(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE, related_name="penalties")
    installment = models.ForeignKey(LoanInstallment, on_delete=models.CASCADE, related_name="penalties")
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"


class LoanClosure(models.Model):
    loan_account = models.OneToOneField(LoanAccount, on_delete=models.CASCADE, related_name="closure")
    closed_date = models.DateField()
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"


class LoanLedger(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE, related_name="ledger_entries")
    transaction_type = models.CharField(max_length=30, choices=LOAN_LEDGER_TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    reference_type = models.CharField(max_length=50, blank=True)
    date = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"
        ordering = ["-date", "-id"]
