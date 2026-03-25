from django.db import models
from django.utils import timezone

from core.choices import (
    ATTENDANCE_ADJUSTMENT_STATUS_CHOICES,
    ATTENDANCE_STATUS_CHOICES,
)
from core.mixins import FiscalYearModelMixin


class Attendance(FiscalYearModelMixin, models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="attendances",
        db_column="employee_id",
    )
    date = models.DateField(default=timezone.localdate)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES, default="pending")
    shift = models.ForeignKey("Shift", on_delete=models.SET_NULL, null=True, blank=True)
    is_late = models.BooleanField(default=False)
    is_half_day = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        unique_together = ("employee", "date")

    def __str__(self) -> str:
        return f"{self.employee} - {self.date} - {self.status}"


class AttendanceAdjustment(FiscalYearModelMixin, models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name="adjustments")
    new_check_in = models.TimeField(null=True, blank=True)
    new_check_out = models.TimeField(null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_ADJUSTMENT_STATUS_CHOICES,
        default="pending",
    )
    requested_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="attendance_requests",
    )
    approved_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_approvals",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.attendance.employee} adjustment on {self.attendance.date}"
