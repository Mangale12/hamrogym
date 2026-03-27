from django.db import models
from core.choices import LEAVE_ACCRUAL_TYPE_CHOICES


class LeaveType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_paid = models.BooleanField(default=False)
    is_carry_forward = models.BooleanField(default=False)
    is_encashable = models.BooleanField(default=False)
    requires_attachment = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False)
    max_days_per_year = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default="#FFFFFF")  # Default to white
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class LeavePolicy(models.Model):
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="policies")

    employment_type = models.ForeignKey("EmploymentType", on_delete=models.CASCADE, related_name="leave_policies")

    days_allowed = models.DecimalField(max_digits=5, decimal_places=2)

    accrual_type = models.CharField(max_length=20, choices=LEAVE_ACCRUAL_TYPE_CHOICES)

    accrual_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    carry_forward_limit = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    carry_forward_expiry_days = models.IntegerField(default=0)

    max_consecutive_days = models.IntegerField(null=True, blank=True)

    min_service_days = models.IntegerField(default=0)

    allow_half_day = models.BooleanField(default=True)

    allow_negative_balance = models.BooleanField(default=False)

    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["leave_type", "employment_type"], name="unique_leave_policy")
        ]

    def __str__(self) -> str:
        return f"{self.leave_type} - {self.employment_type}"
