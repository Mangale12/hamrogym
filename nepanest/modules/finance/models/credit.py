from __future__ import annotations

from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from nepanest.common.mixins import ActiveRemarksModelMixin, FiscalYearBranchModelMixin, TimeStampedModelMixin


ZERO = Decimal("0.00")
HUNDRED = Decimal("100.00")


class CreditDocumentType(models.TextChoices):
    OPENING = "opening", "Opening"
    INVOICE = "invoice", "Invoice"
    BILL = "bill", "Bill"
    PAYMENT = "payment", "Payment"
    CREDIT_NOTE = "credit_note", "Credit Note"
    DEBIT_NOTE = "debit_note", "Debit Note"
    JOURNAL = "journal", "Journal"
    ADJUSTMENT = "adjustment", "Adjustment"


class CreditPolicy(TimeStampedModelMixin, FiscalYearBranchModelMixin, ActiveRemarksModelMixin):
    name = models.CharField(max_length=120, unique=True)
    allow_over_limit = models.BooleanField(default=False)
    over_limit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=ZERO)
    block_sales = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        app_label = "finance"
        ordering = ["name", "id"]

    def clean(self):
        errors = {}

        if self.over_limit_percentage < ZERO or self.over_limit_percentage > HUNDRED:
            errors["over_limit_percentage"] = "Over limit percentage must be between 0 and 100."

        if not self.allow_over_limit and self.over_limit_percentage != ZERO:
            errors["over_limit_percentage"] = "Over limit percentage must be 0 when over-limit credit is not allowed."

        if self.is_default:
            queryset = type(self).objects.filter(
                is_default=True,
                branch_id=self.branch_id,
                fiscal_year_id=self.fiscal_year_id,
            )
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                errors["is_default"] = "Only one default credit policy is allowed per branch and fiscal year."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.name = (self.name or "").strip()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class CreditLimit(TimeStampedModelMixin, FiscalYearBranchModelMixin, ActiveRemarksModelMixin):
    party = models.OneToOneField(
        "core.Party",
        on_delete=models.CASCADE,
        related_name="credit_limit",
    )
    policy = models.ForeignKey(
        "finance.CreditPolicy",
        on_delete=models.PROTECT,
        related_name="credit_limits",
        null=True,
        blank=True,
    )
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=ZERO)
    used_credit = models.DecimalField(max_digits=14, decimal_places=2, default=ZERO, editable=False)

    class Meta:
        app_label = "finance"
        ordering = ["party__name", "id"]

    def clean(self):
        errors = {}

        if self.credit_limit < ZERO:
            errors["credit_limit"] = "Credit limit cannot be negative."

        if self.used_credit < ZERO:
            errors["used_credit"] = "Used credit cannot be negative."

        if self.policy_id and not self.policy.is_active:
            errors["policy"] = "Inactive credit policies cannot be assigned."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        result = super().save(*args, **kwargs)
        financial = getattr(self.party, "financial", None)
        if financial and financial.credit_limit != self.credit_limit:
            financial.credit_limit = self.credit_limit
            financial.save(update_fields=["credit_limit"])
        return result

    @property
    def available_credit(self) -> Decimal:
        return (self.credit_limit or ZERO) - (self.used_credit or ZERO)

    def __str__(self) -> str:
        return f"{self.party} - {self.credit_limit:.2f}"


class CreditTransaction(TimeStampedModelMixin, FiscalYearBranchModelMixin):
    party = models.ForeignKey(
        "core.Party",
        on_delete=models.CASCADE,
        related_name="credit_transactions",
    )
    document_type = models.CharField(max_length=50, choices=CreditDocumentType.choices)
    document_id = models.CharField(max_length=50, blank=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="finance_credit_transactions",
    )
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    source_object = GenericForeignKey("content_type", "object_id")
    transaction_date = models.DateField(default=timezone.localdate)
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=ZERO)
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=ZERO)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2, editable=False)
    is_system_generated = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)

    class Meta:
        app_label = "finance"
        ordering = ["transaction_date", "id"]

    def clean(self):
        errors = {}

        if self.debit < ZERO:
            errors["debit"] = "Debit cannot be negative."

        if self.credit < ZERO:
            errors["credit"] = "Credit cannot be negative."

        if self.debit == ZERO and self.credit == ZERO:
            errors["debit"] = "Either debit or credit must be greater than zero."

        if self.debit > ZERO and self.credit > ZERO:
            errors["credit"] = "Debit and credit cannot both be greater than zero in one transaction."

        if bool(self.content_type_id) != bool(self.object_id):
            errors["content_type"] = "Both content type and object id are required to link a source document."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.document_id = (self.document_id or "").strip()
        self.remarks = (self.remarks or "").strip()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.party} - {self.document_type} - {self.balance_after:.2f}"
