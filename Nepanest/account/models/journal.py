from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.mixins import ActiveRemarksModelMixin, FiscalYearBranchModelMixin, TimeStampedModelMixin, UserAuditModelMixin
from core.mixins.erp import OrganizationBranchModelMixin


class JournalEntryStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    POSTED = "posted", "Posted"
    CANCELLED = "cancelled", "Cancelled"


class PartnerType(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    VENDOR = "vendor", "Vendor"


class JournalEntrySide(models.TextChoices):
    DEBIT = "debit", "Debit"
    CREDIT = "credit", "Credit"


class JournalEntry(
    TimeStampedModelMixin,
    UserAuditModelMixin,
    FiscalYearBranchModelMixin,
    ActiveRemarksModelMixin,
    OrganizationBranchModelMixin,
):
    entry_no = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField(default=timezone.localdate)
    voucher_type = models.ForeignKey(
        "account.VoucherType",
        on_delete=models.PROTECT,
        related_name="journal_entries",
    )
    reference_no = models.CharField(max_length=100, blank=True)
    narration = models.TextField(blank=True)
    total_debit = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), editable=False)
    total_credit = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), editable=False)
    status = models.CharField(max_length=20, choices=JournalEntryStatus.choices, default=JournalEntryStatus.DRAFT)
    posted_at = models.DateTimeField(null=True, blank=True, editable=False)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_posted_journal_entries",
    )
    cancelled_at = models.DateTimeField(null=True, blank=True, editable=False)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_cancelled_journal_entries",
    )

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self) -> str:
        return self.entry_no or "New Journal Entry"

    def delete(self, *args, **kwargs):
        from ..services.journal_service import ensure_journal_entry_can_delete

        ensure_journal_entry_can_delete(self)
        return super().delete(*args, **kwargs)


class JournalLine(models.Model):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    account = models.ForeignKey(
        "account.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="journal_lines",
    )
    description = models.CharField(max_length=255, blank=True)
    entry_side = models.CharField(max_length=10, choices=JournalEntrySide.choices, default=JournalEntrySide.DEBIT)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    partner_type = models.CharField(max_length=20, choices=PartnerType.choices, blank=True)
    partner_id = models.PositiveBigIntegerField(null=True, blank=True)
    cost_center = models.CharField(max_length=120, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        account_label = getattr(self.account, "name", "") or "Account"
        return f"{account_label} ({self.entry_side}:{self.amount})"

    def clean(self):
        from ..services.journal_service import validate_journal_line

        validate_journal_line(self)


class LedgerPosting(models.Model):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="ledger_postings",
    )
    journal_line = models.ForeignKey(
        JournalLine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_postings",
    )
    voucher_type = models.ForeignKey(
        "account.VoucherType",
        on_delete=models.PROTECT,
        related_name="ledger_postings",
    )
    account = models.ForeignKey(
        "account.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="ledger_postings",
    )
    entry_no = models.CharField(max_length=50)
    posting_date = models.DateField()
    reference_no = models.CharField(max_length=100, blank=True)
    narration = models.TextField(blank=True)
    description = models.CharField(max_length=255, blank=True)
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    partner_type = models.CharField(max_length=20, choices=PartnerType.choices, blank=True)
    partner_id = models.PositiveBigIntegerField(null=True, blank=True)
    cost_center = models.CharField(max_length=120, blank=True)
    line_order = models.PositiveIntegerField(default=0)
    is_reversal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["posting_date", "entry_no", "line_order", "id"]

    def __str__(self) -> str:
        return f"{self.entry_no} - {self.account}"
