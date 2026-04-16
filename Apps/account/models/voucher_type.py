from django.db import models
from django.core.exceptions import ValidationError

from core.mixins import TimeStampedModelMixin, UserAuditModelMixin
from core.mixins.erp import OrganizationBranchModelMixin


CATEGORY_CHOICES = (
    ("cash", "Cash"),
    ("bank", "Bank"),
    ("journal", "Journal"),
    ("sales", "Sales"),
    ("purchase", "Purchase"),
    ("adjustment", "Adjustment"),
)

NATURE_CHOICES = (
    ("debit_based", "Debit Based"),
    ("credit_based", "Credit Based"),
    ("both", "Both"),
)


class VoucherType(TimeStampedModelMixin, UserAuditModelMixin, OrganizationBranchModelMixin):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="journal")
    nature = models.CharField(max_length=20, choices=NATURE_CHOICES, default="both")
    affects_cash = models.BooleanField(default=False)
    affects_bank = models.BooleanField(default=False)
    auto_numbering = models.BooleanField(default=True)
    prefix = models.CharField(max_length=20, blank=True)
    last_number = models.PositiveIntegerField(default=0)
    requires_reference = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False)
    allow_negative = models.BooleanField(default=False)
    is_system_generated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(fields=["name", "branch"], name="unique_account_voucher_type_name_branch"),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        self.code = (self.code or "").strip().upper()
        self.name = (self.name or "").strip()
        self.prefix = (self.prefix or "").strip().upper()
        if self.auto_numbering and not self.prefix:
            self.prefix = f"{self.code}-"
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        errors = {}
        if self.last_number < 0:
            errors["last_number"] = "Last number cannot be negative."
        if self.auto_numbering and not (self.prefix or "").strip():
            errors["prefix"] = "Prefix is required when auto numbering is enabled."
        if errors:
            raise ValidationError(errors)
