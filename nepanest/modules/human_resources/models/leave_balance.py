from django.db import models

from core.choices import LEAVE_LEDGER_CHANGE_TYPE_CHOICES


class LeaveBalance(models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="leave_balances",
        db_column="employee_id",
    )
    leave_type = models.ForeignKey(
        "LeaveType",
        on_delete=models.CASCADE,
        related_name="balances",
    )
    year = models.PositiveIntegerField()
    opening_balance = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    accrued = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    used = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    encashed = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["-year", "employee__employee_id", "leave_type__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "leave_type", "year"],
                name="unique_leave_balance_employee_type_year",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.employee} - {self.leave_type} ({self.year})"


class LeaveAccrual(models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="leave_accruals",
        db_column="employee_id",
    )
    leave_type = models.ForeignKey(
        "LeaveType",
        on_delete=models.CASCADE,
        related_name="accruals",
    )
    policy = models.ForeignKey(
        "LeavePolicy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accruals",
    )
    accrual_date = models.DateField()
    days_added = models.DecimalField(max_digits=7, decimal_places=2)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"
        ordering = ["-accrual_date", "-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "leave_type", "policy", "accrual_date"],
                name="unique_leave_accrual_employee_type_policy_date",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.employee} - {self.leave_type} accrual on {self.accrual_date}"


class LeaveLedger(models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="leave_ledger_entries",
        db_column="employee_id",
    )
    leave_type = models.ForeignKey(
        "LeaveType",
        on_delete=models.CASCADE,
        related_name="ledger_entries",
    )
    year = models.PositiveIntegerField()
    change_type = models.CharField(max_length=50, choices=LEAVE_LEDGER_CHANGE_TYPE_CHOICES)
    days = models.DecimalField(max_digits=7, decimal_places=2)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.PositiveBigIntegerField(null=True, blank=True)
    balance_after = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "hr"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["employee", "leave_type", "year"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.employee} - {self.leave_type} - {self.change_type} ({self.days})"
