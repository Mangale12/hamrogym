from django.conf import settings
from django.db import models

from core.choices import APPROVAL_STATUS_CHOICES
from nepanest.common.mixins import FiscalYearModelMixin


class OvertimeRequest(FiscalYearModelMixin, models.Model):
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="overtime_requests",
        db_column="employee_id",
    )
    overtime_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    requested_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default="pending",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="overtime_requests_created",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="overtime_requests_approved",
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["-overtime_date", "-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.employee} overtime request on {self.overtime_date}"


class OvertimeRecord(FiscalYearModelMixin, models.Model):
    request = models.OneToOneField(
        OvertimeRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="overtime_record",
    )
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="overtime_records",
        db_column="employee_id",
    )
    overtime_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2)
    overtime_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    overtime_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default="approved",
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["-overtime_date", "-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.employee} overtime record on {self.overtime_date}"
