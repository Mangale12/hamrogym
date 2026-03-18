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
