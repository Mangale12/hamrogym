from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from nepanest.common.mixins.erp import FiscalYearBranchModelMixin

ZERO = Decimal("0")
HUNDRED = Decimal("100")


class DiscountType(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    FIXED = "fixed", "Fixed Amount"


class DiscountScope(models.TextChoices):
    LINE = "line", "Line"
    DOCUMENT = "document", "Document"


class Discount(FiscalYearBranchModelMixin):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)

    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
    )

    value = models.DecimalField(max_digits=10, decimal_places=4, default=ZERO)

    scope = models.CharField(
        max_length=20,
        choices=DiscountScope.choices,
        default=DiscountScope.LINE,
    )

    class Meta:
        app_label = "finance"
        ordering = ["name", "id"]

    def clean(self):
        if self.discount_type == DiscountType.PERCENTAGE:
            if self.value < ZERO or self.value > HUNDRED:
                raise ValidationError({"value": "Must be between 0 and 100"})
        else:
            if self.value <= ZERO:
                raise ValidationError({"value": "Must be greater than 0"})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class DiscountRule(FiscalYearBranchModelMixin):
    name = models.CharField(max_length=120)
    discount = models.ForeignKey("Discount", on_delete=models.CASCADE)
    # Conditions
    party_type = models.ForeignKey("core.PartyType", null=True, blank=True, on_delete=models.SET_NULL)
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    priority = models.PositiveIntegerField(default=1)

    class Meta:
        app_label = "finance"
        ordering = ["priority", "name", "id"]

    def clean(self):
        errors = {}

        if self.min_quantity is not None and self.min_quantity < ZERO:
            errors["min_quantity"] = "Min quantity cannot be negative."

        if self.min_amount is not None and self.min_amount < ZERO:
            errors["min_amount"] = "Min amount cannot be negative."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.discount} - {self.name}"
