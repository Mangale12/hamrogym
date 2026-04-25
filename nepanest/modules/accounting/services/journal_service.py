from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import (
    ChartOfAccount,
    JournalEntry,
    JournalEntrySide,
    JournalEntryStatus,
    JournalLine,
    LedgerPosting,
    VoucherType,
)


ZERO = Decimal("0.00")


def to_decimal(value) -> Decimal:
    if value in (None, ""):
        return ZERO
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return ZERO


def ensure_journal_entry_can_delete(entry: JournalEntry) -> None:
    if entry.status != JournalEntryStatus.DRAFT:
        raise ValidationError("Only draft journal entries can be deleted.")


def prepare_journal_entry_for_save(entry: JournalEntry) -> JournalEntry:
    errors = {}

    if entry.pk:
        current = JournalEntry.objects.filter(pk=entry.pk).values("status", "entry_no").first()
        if current and current["status"] != JournalEntryStatus.DRAFT:
            raise ValidationError("Only draft journal entries can be edited.")
        if current and current["entry_no"] and not entry.entry_no:
            entry.entry_no = current["entry_no"]

    entry.reference_no = (entry.reference_no or "").strip()
    entry.narration = (entry.narration or "").strip()
    entry.entry_no = (entry.entry_no or "").strip().upper()
    entry.status = entry.status or JournalEntryStatus.DRAFT

    if not entry.voucher_type_id:
        errors["voucher_type"] = "Voucher type is required."
    else:
        voucher_type = VoucherType.objects.select_for_update().get(pk=entry.voucher_type_id)
        if not voucher_type.is_active:
            errors["voucher_type"] = "Inactive voucher types cannot be used."
        elif voucher_type.auto_numbering:
            if not entry.entry_no or (not entry.pk and entry.entry_no.startswith("AUTO")):
                entry.entry_no = _generate_next_entry_no(voucher_type)
        elif not entry.entry_no:
            errors["entry_no"] = "Entry number is required because auto numbering is disabled."

    if errors:
        raise ValidationError(errors)
    return entry


def validate_journal_line(line: JournalLine) -> JournalLine:
    errors = {}
    amount = to_decimal(line.amount)
    line.amount = amount
    line.description = (line.description or "").strip()
    line.cost_center = (line.cost_center or "").strip()

    account = None
    if not line.account_id:
        errors["account"] = "Ledger account is required."
    else:
        try:
            account = line.account if isinstance(line.account, ChartOfAccount) else ChartOfAccount.objects.get(pk=line.account_id)
        except ChartOfAccount.DoesNotExist:
            errors["account"] = "Selected ledger account was not found."
        else:
            if not account.is_ledger:
                errors["account"] = "Only ledger accounts can be used in journal lines."
            elif not account.is_active:
                errors["account"] = "Inactive ledger accounts cannot be used."

    if line.entry_side not in {JournalEntrySide.DEBIT, JournalEntrySide.CREDIT}:
        errors["entry_side"] = "Entry side must be either debit or credit."

    if amount <= ZERO:
        errors["amount"] = "Amount must be greater than zero."

    if errors:
        raise ValidationError(errors)
    return line


def validate_journal_entry(entry: JournalEntry, *, lines=None):
    resolved_lines = list(lines) if lines is not None else list(
        entry.lines.select_related("account").order_by("sort_order", "id")
    )
    errors = {}

    if len(resolved_lines) < 2:
        errors["journal_lines"] = ["At least two journal lines are required."]

    total_debit = ZERO
    total_credit = ZERO
    for index, line in enumerate(resolved_lines, start=1):
        try:
            validate_journal_line(line)
        except ValidationError as exc:
            messages = []
            if hasattr(exc, "message_dict"):
                for value in exc.message_dict.values():
                    if isinstance(value, list):
                        messages.extend(str(item) for item in value)
                    else:
                        messages.append(str(value))
            else:
                messages.extend(exc.messages)
            errors[f"line_{index}"] = messages
        line_amount = to_decimal(line.amount)
        if line.entry_side == JournalEntrySide.DEBIT:
            total_debit += line_amount
        else:
            total_credit += line_amount

    if total_debit <= ZERO or total_credit <= ZERO:
        errors["total_debit"] = ["Total debit and total credit must be greater than zero."]

    if total_debit != total_credit:
        errors["total_credit"] = ["Total debit and total credit must be equal."]

    if errors:
        raise ValidationError(errors)

    return {
        "lines": resolved_lines,
        "total_debit": total_debit.quantize(Decimal("0.01")),
        "total_credit": total_credit.quantize(Decimal("0.01")),
    }


def synchronize_journal_entry(entry: JournalEntry) -> JournalEntry:
    result = validate_journal_entry(entry)
    entry.total_debit = result["total_debit"]
    entry.total_credit = result["total_credit"]
    JournalEntry.objects.filter(pk=entry.pk).update(
        total_debit=entry.total_debit,
        total_credit=entry.total_credit,
    )
    return entry


@transaction.atomic
def post_journal_entry(entry: JournalEntry, *, user=None) -> JournalEntry:
    locked_entry = (
        JournalEntry.objects.select_for_update()
        .select_related("voucher_type")
        .get(pk=entry.pk)
    )

    if locked_entry.status == JournalEntryStatus.POSTED:
        raise ValidationError("This journal entry is already posted.")
    if locked_entry.status == JournalEntryStatus.CANCELLED:
        raise ValidationError("Cancelled journal entries cannot be posted.")

    result = validate_journal_entry(locked_entry)
    _replace_ledger_postings(locked_entry, result["lines"], is_reversal=False)

    locked_entry.total_debit = result["total_debit"]
    locked_entry.total_credit = result["total_credit"]
    locked_entry.status = JournalEntryStatus.POSTED
    locked_entry.posted_at = timezone.now()
    locked_entry.posted_by = user
    locked_entry.cancelled_at = None
    locked_entry.cancelled_by = None
    locked_entry.save(
        update_fields=[
            "total_debit",
            "total_credit",
            "status",
            "posted_at",
            "posted_by",
            "cancelled_at",
            "cancelled_by",
            "updated_at",
        ]
    )
    return locked_entry


@transaction.atomic
def cancel_journal_entry(entry: JournalEntry, *, user=None) -> JournalEntry:
    locked_entry = (
        JournalEntry.objects.select_for_update()
        .select_related("voucher_type")
        .get(pk=entry.pk)
    )

    if locked_entry.status == JournalEntryStatus.CANCELLED:
        raise ValidationError("This journal entry is already cancelled.")

    result = validate_journal_entry(locked_entry)
    if locked_entry.status == JournalEntryStatus.POSTED:
        _append_reversal_postings(locked_entry, result["lines"])

    locked_entry.total_debit = result["total_debit"]
    locked_entry.total_credit = result["total_credit"]
    locked_entry.status = JournalEntryStatus.CANCELLED
    locked_entry.cancelled_at = timezone.now()
    locked_entry.cancelled_by = user
    locked_entry.save(
        update_fields=[
            "total_debit",
            "total_credit",
            "status",
            "cancelled_at",
            "cancelled_by",
            "updated_at",
        ]
    )
    return locked_entry


def _generate_next_entry_no(voucher_type: VoucherType) -> str:
    voucher_type.last_number = (voucher_type.last_number or 0) + 1
    voucher_type.save(update_fields=["last_number", "updated_at"])
    return f"{voucher_type.prefix}{voucher_type.last_number:05d}"


def _replace_ledger_postings(entry: JournalEntry, lines, *, is_reversal: bool) -> None:
    entry.ledger_postings.all().delete()
    _bulk_create_ledger_postings(entry, lines, is_reversal=is_reversal)


def _append_reversal_postings(entry: JournalEntry, lines) -> None:
    if entry.ledger_postings.filter(is_reversal=True).exists():
        raise ValidationError("This journal entry is already reversed.")
    _bulk_create_ledger_postings(entry, lines, is_reversal=True)


def _bulk_create_ledger_postings(entry: JournalEntry, lines, *, is_reversal: bool) -> None:
    postings = []
    for index, line in enumerate(lines, start=1):
        is_debit_line = line.entry_side == JournalEntrySide.DEBIT
        debit_amount = to_decimal(line.amount) if (is_debit_line and not is_reversal) or (not is_debit_line and is_reversal) else ZERO
        credit_amount = to_decimal(line.amount) if (not is_debit_line and not is_reversal) or (is_debit_line and is_reversal) else ZERO
        postings.append(
            LedgerPosting(
                journal_entry=entry,
                journal_line=line,
                voucher_type=entry.voucher_type,
                account=line.account,
                entry_no=entry.entry_no,
                posting_date=entry.date,
                reference_no=entry.reference_no,
                narration=entry.narration,
                description=line.description,
                debit_amount=debit_amount,
                credit_amount=credit_amount,
                partner_type=line.partner_type,
                partner_id=line.partner_id,
                cost_center=line.cost_center,
                line_order=line.sort_order or index,
                is_reversal=is_reversal,
            )
        )
    if postings:
        LedgerPosting.objects.bulk_create(postings)
