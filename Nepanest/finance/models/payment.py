from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.mixins.erp import ERPBaseModel


ZERO = Decimal("0.00")


class PaymentType(models.TextChoices):
    RECEIVE = "receive", "Receive"
    PAY = "pay", "Pay"


class PaymentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    POSTED = "posted", "Posted"
    CANCELLED = "cancelled", "Cancelled"


class Payment(ERPBaseModel):
    payment_no = models.CharField(max_length=50, unique=True, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True)
    reference_date = models.DateField(null=True, blank=True)
    payment_type = models.CharField(max_length=10, choices=PaymentType.choices)
    party = models.ForeignKey(
        "core.Party",
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
    )
    billing_profile = models.ForeignKey(
        "billing.BillingProfile",
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
    )
    payment_method = models.ForeignKey(
        "finance.PaymentMethod",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
        related_name="finance_payments",
    )
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"))
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    allocated_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=ZERO,
        editable=False,
    )
    unapplied_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=ZERO,
        editable=False,
    )
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.DRAFT)
    journal_entry = models.OneToOneField(
        "account.JournalEntry",
        on_delete=models.PROTECT,
        related_name="payment",
        null=True,
        blank=True,
    )
    posted_at = models.DateTimeField(null=True, blank=True, editable=False)
    cancelled_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self) -> str:
        return self.payment_no or self.reference or f"Payment #{self.pk}"

    def clean(self):
        errors = {}
        amount = self.amount if self.amount is not None else ZERO
        exchange_rate = self.exchange_rate if self.exchange_rate is not None else ZERO

        if amount <= ZERO:
            errors["amount"] = "Amount must be greater than zero."

        if exchange_rate <= ZERO:
            errors["exchange_rate"] = "Exchange rate must be greater than zero."

        if self.reference_date and self.date and self.reference_date > self.date:
            errors["reference_date"] = "Reference date cannot be later than payment date."

        if self.payment_method_id:
            if not self.payment_method.is_active:
                errors["payment_method"] = "Inactive payment methods cannot be used."
            elif self.payment_method.requires_reference and not (self.reference or "").strip():
                errors["reference"] = "Reference is required for the selected payment method."

        if self.journal_entry_id and self.journal_entry.date != self.date:
            errors["journal_entry"] = "Linked journal entry date must match the payment date."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.payment_no = (self.payment_no or "").strip().upper() or None
        self.reference = (self.reference or "").strip()
        self.full_clean()
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and not self.payment_no:
            prefix = "RCV" if self.payment_type == PaymentType.RECEIVE else "PAY"
            generated_no = f"{prefix}-{self.pk:06d}"
            type(self).objects.filter(pk=self.pk, payment_no__isnull=True).update(payment_no=generated_no)
            self.payment_no = generated_no

    def delete(self, *args, **kwargs):
        from ..services import ensure_payment_can_delete

        ensure_payment_can_delete(self)
        return super().delete(*args, **kwargs)

    @property
    def has_unapplied_balance(self) -> bool:
        return (self.unapplied_amount or ZERO) > ZERO


class PaymentAllocation(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    billing_document = models.ForeignKey(
        "billing.BillingDocument",
        on_delete=models.PROTECT,
        related_name="payment_allocations",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True)
    sequence = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["sequence", "id"]

    def __str__(self) -> str:
        return f"{self.payment} -> {self.billing_document}"

    def clean(self):
        errors = {}
        amount = self.amount if self.amount is not None else ZERO

        if amount <= ZERO:
            errors["amount"] = "Allocation amount must be greater than zero."

        if self.payment_id and self.billing_document_id:
            payment = self.payment
            document = self.billing_document

            if document.document_type == "proforma":
                errors["billing_document"] = "Proforma documents cannot receive payment allocations."
            elif document.status in {"draft", "cancelled"}:
                errors["billing_document"] = "Only confirmed or active billing documents can be allocated."

            if payment.currency_id and document.currency_id and payment.currency_id != document.currency_id:
                errors["billing_document"] = "Payment currency must match the selected billing document currency."

            if payment.billing_profile_id and document.billing_profile_id != payment.billing_profile_id:
                errors["billing_document"] = "Billing document must belong to the selected billing profile."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.remarks = (self.remarks or "").strip()
        self.full_clean()
        return super().save(*args, **kwargs)

