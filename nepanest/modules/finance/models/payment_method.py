from django.core.exceptions import ValidationError
from django.db import models

from nepanest.common.mixins import ActiveRemarksModelMixin, TimeStampedModelMixin


class PaymentMethodCategory(models.TextChoices):
    CASH = "cash", "Cash"
    BANK = "bank", "Bank"
    WALLET = "wallet", "Digital Wallet"
    QR = "qr", "QR Payment"
    CARD = "card", "Card"
    CHEQUE = "cheque", "Cheque"


class PaymentMethod(TimeStampedModelMixin, ActiveRemarksModelMixin):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(
        max_length=20,
        choices=PaymentMethodCategory.choices,
        default=PaymentMethodCategory.BANK,
    )
    provider = models.CharField(max_length=120, blank=True)
    sequence = models.PositiveIntegerField(default=1)
    is_digital = models.BooleanField(default=False)
    supports_online = models.BooleanField(default=False)
    supports_qr = models.BooleanField(default=False)
    requires_reference = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)

    class Meta:
        app_label = "finance"
        ordering = ["sequence", "name", "id"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def clean(self):
        errors = {}

        if self.sequence < 0:
            errors["sequence"] = "Sequence cannot be negative."

        if self.supports_qr and self.category not in {
            PaymentMethodCategory.QR,
            PaymentMethodCategory.WALLET,
            PaymentMethodCategory.BANK,
        }:
            errors["supports_qr"] = "QR support is only valid for bank, wallet, or QR methods."

        if self.is_default:
            queryset = type(self).objects.filter(is_default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                errors["is_default"] = "Only one payment method can be marked as default."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.code = (self.code or "").strip().upper()
        self.name = (self.name or "").strip()
        self.provider = (self.provider or "").strip()
        self.full_clean()
        return super().save(*args, **kwargs)
