from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from nepanest.modules.accounting.models import JournalEntryStatus
from nepanest.modules.accounting.services import cancel_journal_entry, post_journal_entry
from nepanest.modules.billing.models import BillingDocument

from ..models import Payment, PaymentAllocation, PaymentStatus, PaymentType


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


def ensure_payment_can_delete(payment: Payment) -> None:
    if payment.status != PaymentStatus.DRAFT:
        raise ValidationError("Only draft payments can be deleted.")


def prepare_payment_for_save(payment: Payment) -> Payment:
    errors = {}

    if payment.pk:
        current = Payment.objects.filter(pk=payment.pk).values("status", "payment_no").first()
        if current and current["status"] != PaymentStatus.DRAFT:
            raise ValidationError("Only draft payments can be edited.")
        if current and current["payment_no"] and not payment.payment_no:
            payment.payment_no = current["payment_no"]

    payment.reference = (payment.reference or "").strip()
    payment.payment_no = (payment.payment_no or "").strip().upper() or None
    payment.status = payment.status or PaymentStatus.DRAFT
    payment.amount = to_decimal(payment.amount)
    payment.allocated_amount = to_decimal(payment.allocated_amount)
    payment.unapplied_amount = to_decimal(payment.unapplied_amount or payment.amount)

    if payment.journal_entry_id:
        if payment.journal_entry.status == JournalEntryStatus.CANCELLED:
            errors["journal_entry"] = "Cancelled journal entries cannot be linked to payments."

    if errors:
        raise ValidationError(errors)
    return payment


def validate_payment(payment: Payment, *, allocations=None):
    resolved_allocations = list(allocations) if allocations is not None else list(
        payment.allocations.select_related("billing_document", "billing_document__billing_profile", "billing_document__currency")
    )
    errors = {}
    total_allocated = ZERO
    document_ids = set()
    billing_profile_id = payment.billing_profile_id

    if not payment.party_id and not billing_profile_id and not resolved_allocations:
        errors["party"] = ["Select a party, billing profile, or allocate the payment to at least one document."]

    for index, allocation in enumerate(resolved_allocations, start=1):
        document = allocation.billing_document
        line_errors = []
        allocation.amount = to_decimal(allocation.amount)
        total_allocated += allocation.amount

        if document_ids and document.pk in document_ids:
            line_errors.append("The same billing document can only be allocated once in a payment.")
        document_ids.add(document.pk)

        if not billing_profile_id:
            billing_profile_id = document.billing_profile_id
        elif document.billing_profile_id != billing_profile_id:
            line_errors.append("All allocations in a payment must belong to the same billing profile.")

        expected_payment_type = _resolve_payment_type_for_document(document)
        if expected_payment_type and payment.payment_type != expected_payment_type:
            line_errors.append(
                f"{document.get_document_type_display()} requires a {expected_payment_type} payment."
            )

        available_amount = _available_amount_for_document(document, exclude_payment_id=payment.pk)
        if allocation.amount > available_amount:
            line_errors.append(
                f"Only {available_amount:.2f} is currently available to allocate against {document.document_number}."
            )

        if line_errors:
            errors[f"allocation_{index}"] = line_errors

    total_allocated = total_allocated.quantize(Decimal("0.01"))
    payment_amount = to_decimal(payment.amount)

    if total_allocated > payment_amount:
        errors["amount"] = ["Allocated amount cannot exceed the payment amount."]

    if payment.billing_profile_id and billing_profile_id and payment.billing_profile_id != billing_profile_id:
        errors["billing_profile"] = ["Selected billing profile does not match the allocated documents."]

    if errors:
        raise ValidationError(errors)

    if not payment.billing_profile_id and billing_profile_id:
        payment.billing_profile_id = billing_profile_id

    return {
        "allocations": resolved_allocations,
        "allocated_amount": total_allocated,
        "unapplied_amount": (payment_amount - total_allocated).quantize(Decimal("0.01")),
    }


def synchronize_payment(payment: Payment) -> Payment:
    result = validate_payment(payment)
    payment.allocated_amount = result["allocated_amount"]
    payment.unapplied_amount = result["unapplied_amount"]
    Payment.objects.filter(pk=payment.pk).update(
        billing_profile_id=payment.billing_profile_id,
        allocated_amount=payment.allocated_amount,
        unapplied_amount=payment.unapplied_amount,
    )
    if payment.status == PaymentStatus.POSTED:
        _sync_billing_documents_for_payment(payment)
    return payment


@transaction.atomic
def post_payment(payment: Payment, *, user=None) -> Payment:
    locked_payment = (
        Payment.objects.select_for_update()
        .select_related("journal_entry")
        .get(pk=payment.pk)
    )

    if locked_payment.status == PaymentStatus.POSTED:
        raise ValidationError("This payment is already posted.")
    if locked_payment.status == PaymentStatus.CANCELLED:
        raise ValidationError("Cancelled payments cannot be posted.")

    result = validate_payment(locked_payment)
    locked_payment.billing_profile_id = locked_payment.billing_profile_id or payment.billing_profile_id
    locked_payment.allocated_amount = result["allocated_amount"]
    locked_payment.unapplied_amount = result["unapplied_amount"]
    locked_payment.status = PaymentStatus.POSTED
    locked_payment.posted_at = timezone.now()
    locked_payment.cancelled_at = None
    locked_payment.save(
        update_fields=[
            "billing_profile",
            "allocated_amount",
            "unapplied_amount",
            "status",
            "posted_at",
            "cancelled_at",
            "updated_at",
        ]
    )

    if locked_payment.journal_entry_id:
        journal = locked_payment.journal_entry
        if journal.status == JournalEntryStatus.CANCELLED:
            raise ValidationError("Linked journal entry is cancelled and cannot be posted with this payment.")
        if journal.status != JournalEntryStatus.POSTED:
            post_journal_entry(journal, user=user)

    _sync_billing_documents_for_payment(locked_payment)
    return locked_payment


@transaction.atomic
def cancel_payment(payment: Payment, *, user=None) -> Payment:
    locked_payment = (
        Payment.objects.select_for_update()
        .select_related("journal_entry")
        .get(pk=payment.pk)
    )

    if locked_payment.status == PaymentStatus.CANCELLED:
        raise ValidationError("This payment is already cancelled.")

    if locked_payment.journal_entry_id and locked_payment.journal_entry.status != JournalEntryStatus.CANCELLED:
        cancel_journal_entry(locked_payment.journal_entry, user=user)

    result = validate_payment(locked_payment)
    locked_payment.allocated_amount = result["allocated_amount"]
    locked_payment.unapplied_amount = result["unapplied_amount"]
    locked_payment.status = PaymentStatus.CANCELLED
    locked_payment.cancelled_at = timezone.now()
    locked_payment.save(
        update_fields=[
            "allocated_amount",
            "unapplied_amount",
            "status",
            "cancelled_at",
            "updated_at",
        ]
    )

    _sync_billing_documents_for_payment(locked_payment)
    return locked_payment


def _resolve_payment_type_for_document(document: BillingDocument) -> str | None:
    if document.document_type == "invoice":
        return PaymentType.RECEIVE
    if document.document_type == "bill":
        return PaymentType.PAY
    if document.document_type == "debit_note":
        return PaymentType.PAY if document.billing_profile.billing_type == "vendor" else PaymentType.RECEIVE
    if document.document_type == "credit_note":
        return PaymentType.RECEIVE if document.billing_profile.billing_type == "vendor" else PaymentType.PAY
    return None


def _available_amount_for_document(document: BillingDocument, *, exclude_payment_id=None) -> Decimal:
    posted_allocations = PaymentAllocation.objects.filter(
        billing_document=document,
        payment__status=PaymentStatus.POSTED,
    )
    if exclude_payment_id:
        posted_allocations = posted_allocations.exclude(payment_id=exclude_payment_id)

    allocated_total = posted_allocations.aggregate(
        total=Coalesce(Sum("amount"), ZERO)
    )["total"] or ZERO
    available = to_decimal(document.total_amount) - to_decimal(allocated_total)
    return max(available, ZERO)


def _sync_billing_documents_for_payment(payment: Payment) -> None:
    document_ids = list(payment.allocations.values_list("billing_document_id", flat=True))
    if not document_ids:
        return

    for document in BillingDocument.objects.filter(pk__in=document_ids).select_related("billing_profile"):
        posted_total = PaymentAllocation.objects.filter(
            billing_document=document,
            payment__status=PaymentStatus.POSTED,
        ).aggregate(total=Coalesce(Sum("amount"), ZERO))["total"] or ZERO
        posted_total = to_decimal(posted_total)
        total_amount = to_decimal(document.total_amount)
        due_amount = max(total_amount - posted_total, ZERO)

        if posted_total <= ZERO:
            next_status = _resolve_open_document_status(document)
        elif due_amount <= ZERO:
            next_status = "paid"
        else:
            next_status = "partially_paid"

        BillingDocument.objects.filter(pk=document.pk).update(
            paid_amount=posted_total,
            due_amount=due_amount,
            status=next_status,
        )


def _resolve_open_document_status(document: BillingDocument) -> str:
    if document.status == "cancelled":
        return document.status
    if document.due_date and document.due_date < timezone.localdate():
        return "overdue"
    return "confirmed"
