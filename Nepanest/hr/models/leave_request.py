from django.db import models
from django.conf import settings

from core.choices import APPROVAL_STATUS_CHOICES, LEAVE_HALF_DAY_TYPE_CHOICES


class LeaveRequest(models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="leave_requests",
        db_column="employee_id",
    )
    leave_type = models.ForeignKey("LeaveType", on_delete=models.CASCADE, related_name="leave_requests")

    start_date = models.DateField()
    end_date = models.DateField()

    total_days = models.DecimalField(max_digits=5, decimal_places=2)

    is_half_day = models.BooleanField(default=False)
    half_day_type = models.CharField(
        max_length=20,
        choices=LEAVE_HALF_DAY_TYPE_CHOICES,
        null=True,
        blank=True,
    )

    reason = models.TextField()

    attachment = models.FileField(upload_to="leave_attachments/", null=True, blank=True)

    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="pending")

    applied_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    cancelled_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_leave_requests")
    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="rejected_leave_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"


class LeaveApproval(models.Model):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name="approvals")

    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    level = models.IntegerField()

    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="pending")

    remarks = models.TextField(blank=True)

    action_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["level", "id"]
        constraints = [
            models.UniqueConstraint(fields=["leave_request", "level"], name="unique_leave_approval_request_level"),
            models.UniqueConstraint(
                fields=["leave_request", "approver", "level"],
                name="unique_leave_approval_request_approver_level",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.leave_request} - Level {self.level}"
