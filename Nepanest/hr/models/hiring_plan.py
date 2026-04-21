from django.db import models

from core.choices import APPROVAL_STATUS_CHOICES
from core.mixins import FiscalYearModelMixin


class HiringPlan(FiscalYearModelMixin, models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        help_text="Name of the hiring plan",
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        null=False,
        blank=False,
        help_text="Code of the hiring plan",
    )
    description = models.TextField(blank=True, help_text="Description of the hiring plan")
    status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default="draft",
        help_text="Status of the hiring plan",
    )
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class HiringPlanItem(models.Model):
    hiring_plan = models.ForeignKey(HiringPlan, on_delete=models.CASCADE, related_name="items")
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="hiring_plan_items")
    department = models.ForeignKey("Department", on_delete=models.CASCADE, related_name="hiring_plan_items")
    designation = models.ForeignKey("Designation", on_delete=models.CASCADE, related_name="hiring_plan_items")
    employeement_type = models.ForeignKey("EmploymentType", on_delete=models.CASCADE, related_name="hiring_plan_items")
    planned_head_count = models.PositiveIntegerField(default=1)
    planned_month = models.PositiveIntegerField(default=1)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("hiring_plan", "branch", "department", "designation", "employeement_type")

    def __str__(self) -> str:
        return f"{self.hiring_plan.name} - {self.branch.name} - {self.department.name} - {self.designation.name} - {self.employeement_type.name}"