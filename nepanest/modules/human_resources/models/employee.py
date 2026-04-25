from django.conf import settings
from django.db import models

from core.choices import EMPLOYEE_TYPE_CHOICES, EMPLOYMENT_STATUS_CHOICES
from .department import Department
from .designation import Designation


class Employee(models.Model):
    EMPLOYEE_TYPE_CHOICES = EMPLOYEE_TYPE_CHOICES
    EMPLOYMENT_STATUS_CHOICES = EMPLOYMENT_STATUS_CHOICES

    organization = models.ForeignKey(
        "core.Organization", on_delete=models.PROTECT, null=True, blank=True
    )
    branch = models.ForeignKey(
        "core.Branch", on_delete=models.PROTECT, null=True, blank=True
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="employee_profile",
    )
    employee_id = models.CharField(max_length=30, unique=True)
    employee_code = models.CharField(max_length=30, blank=True)

    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True, blank=True)
    reporting_manager = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="reportees"
    )
    join_date = models.DateField(null=True, blank=True)
    employee_type = models.CharField(
        max_length=20, choices=EMPLOYEE_TYPE_CHOICES, blank=True
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default="active",
        blank=True,
    )
    shift = models.CharField(max_length=50, blank=True)
    probation_period = models.PositiveIntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hr_employees_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hr_employees_updated",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["employee_id"]

    def __str__(self) -> str:
        return self.full_name or self.employee_id

    @property
    def full_name(self) -> str:
        return (self.user.get_full_name() or self.user.username or "").strip()
