from django.conf import settings
from django.db import models
from django.conf import settings
from core.choices import ATTENDANCE_STATUS_CHOICES
from core.mixins import FiscalYearModelMixin
class Attendance(FiscalYearModelMixin, models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(auto_now=True)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES, default="pending")
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
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES, default="pending")

    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="attendance_requests")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_approvals")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
