from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.mixins import ActiveRemarksModelMixin, FiscalYearBranchModelMixin, TimeStampedModelMixin
from core.models import Currency, PartyType


ZERO = Decimal("0.00")
MAX_PRECISION = 6


class RoundingApplicationScope(models.TextChoices):
    SALES = "sales", "Sales"
    PURCHASE = "purchase", "Purchase"
    BOTH = "both", "Both"


class RoundingMethod(models.TextChoices):
    HALF_UP = "half_up", "Half Up"
    HALF_DOWN = "half_down", "Half Down"
    HALF_EVEN = "half_even", "Half Even"
    UP = "up", "Round Up"
    DOWN = "down", "Round Down"
    CEILING = "ceiling", "Ceiling"
    FLOOR = "floor", "Floor"


class RoundingTarget(models.TextChoices):
    LINE = "line", "Line Amount"
    DOCUMENT = "document", "Document Total"
    TAX = "tax", "Tax Amount"
    GRAND_TOTAL = "grand_total", "Grand Total"
    PAYMENT = "payment", "Payment Amount"


class RoundingDocumentType(models.TextChoices):
    ALL = "all", "All Documents"
    INVOICE = "invoice", "Invoice"
    BILL = "bill", "Bill"
    CREDIT_NOTE = "credit_note", "Credit Note"
    DEBIT_NOTE = "debit_note", "Debit Note"
    PAYMENT = "payment", "Payment"


def scopes_are_compatible(left_scope: str, right_scope: str) -> bool:
    return (
        left_scope in {RoundingApplicationScope.BOTH, right_scope}
        or right_scope in {RoundingApplicationScope.BOTH, left_scope}
    )


def decimal_places(value: Decimal | None) -> int:
    if value is None:
        return 0
    exponent = value.normalize().as_tuple().exponent
    return abs(exponent) if exponent < 0 else 0


class Rounding(TimeStampedModelMixin, FiscalYearBranchModelMixin, ActiveRemarksModelMixin):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    application_scope = models.CharField(
        max_length=20,
        choices=RoundingApplicationScope.choices,
        default=RoundingApplicationScope.BOTH,
    )
    rounding_method = models.CharField(
        max_length=20,
        choices=RoundingMethod.choices,
        default=RoundingMethod.HALF_UP,
    )
    round_on = models.CharField(
        max_length=20,
        choices=RoundingTarget.choices,
        default=RoundingTarget.DOCUMENT,
    )
    precision = models.PositiveSmallIntegerField(default=2)
    increment = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("0.010000"))
    is_cash_rounding = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["name", "id"]

    def clean(self):
        errors = {}

        if self.precision > MAX_PRECISION:
            errors["precision"] = f"Precision cannot exceed {MAX_PRECISION} decimal places."

        if self.increment is None or self.increment <= ZERO:
            errors["increment"] = "Increment must be greater than zero."
        elif decimal_places(self.increment) > self.precision:
            errors["increment"] = "Increment cannot have more decimal places than the selected precision."

        if self.is_cash_rounding and self.round_on == RoundingTarget.LINE:
            errors["round_on"] = "Cash rounding should be applied on document, grand total, or payment level."

        if self.is_default:
            queryset = type(self).objects.filter(
                is_default=True,
                application_scope=self.application_scope,
                branch_id=self.branch_id,
                fiscal_year_id=self.fiscal_year_id,
            )
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                errors["is_default"] = "Only one default rounding is allowed per scope, branch, and fiscal year."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.code = (self.code or "").strip().upper()
        self.name = (self.name or "").strip()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class RoundingRule(TimeStampedModelMixin, FiscalYearBranchModelMixin, ActiveRemarksModelMixin):
    name = models.CharField(max_length=120)
    rounding = models.ForeignKey(
        "finance.Rounding",
        on_delete=models.CASCADE,
        related_name="rules",
    )
    application_scope = models.CharField(
        max_length=20,
        choices=RoundingApplicationScope.choices,
        default=RoundingApplicationScope.BOTH,
    )
    document_type = models.CharField(
        max_length=20,
        choices=RoundingDocumentType.choices,
        default=RoundingDocumentType.ALL,
    )
    party_type = models.ForeignKey(
        PartyType,
        on_delete=models.PROTECT,
        related_name="rounding_rules",
        null=True,
        blank=True,
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="rounding_rules",
        null=True,
        blank=True,
    )
    payment_method = models.ForeignKey(
        "finance.PaymentMethod",
        on_delete=models.PROTECT,
        related_name="rounding_rules",
        null=True,
        blank=True,
    )
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    priority = models.PositiveIntegerField(default=1)
    stop_processing = models.BooleanField(default=False)

    class Meta:
        ordering = ["priority", "name", "id"]

    def clean(self):
        errors = {}

        if self.min_amount is not None and self.min_amount < ZERO:
            errors["min_amount"] = "Min amount cannot be negative."

        if self.max_amount is not None and self.max_amount < ZERO:
            errors["max_amount"] = "Max amount cannot be negative."

        if self.max_amount is not None and self.min_amount is not None and self.max_amount < self.min_amount:
            errors["max_amount"] = "Max amount cannot be less than min amount."

        if self.rounding_id and not scopes_are_compatible(self.rounding.application_scope, self.application_scope):
            errors["application_scope"] = "Rule scope must be compatible with the selected rounding scope."

        if self.document_type == RoundingDocumentType.PAYMENT and self.rounding_id:
            if self.rounding.round_on not in {RoundingTarget.PAYMENT, RoundingTarget.DOCUMENT, RoundingTarget.GRAND_TOTAL}:
                errors["rounding"] = "Payment document rules require a payment/document/grand-total rounding target."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.name = (self.name or "").strip()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.rounding} - {self.name}"

