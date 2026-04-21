from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

from core.models import PartyFinancial

from ..models import CreditLimit, CreditPolicy, CreditTransaction


ZERO = Decimal("0.00")
HUNDRED = Decimal("100.00")


def to_decimal(value) -> Decimal:
    if value in (None, ""):
        return ZERO
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return ZERO


def get_or_create_credit_limit(party, *, branch_id=None, fiscal_year_id=None) -> CreditLimit:
    defaults = {
        "branch_id": branch_id,
        "fiscal_year_id": fiscal_year_id,
        "credit_limit": ZERO,
    }
    financial = PartyFinancial.objects.filter(party=party).first()
    if financial:
        defaults["credit_limit"] = to_decimal(financial.credit_limit)
        defaults["branch_id"] = branch_id or financial.branch_id
        defaults["fiscal_year_id"] = fiscal_year_id or financial.fiscal_year_id

    credit_limit, _created = CreditLimit.objects.get_or_create(
        party=party,
        defaults=defaults,
    )
    return credit_limit


def get_applicable_credit_policy(credit_limit: CreditLimit | None) -> CreditPolicy | None:
    if credit_limit and credit_limit.policy_id:
        return credit_limit.policy

    queryset = CreditPolicy.objects.filter(is_active=True, is_default=True)
    if credit_limit:
        queryset = queryset.filter(branch_id=credit_limit.branch_id, fiscal_year_id=credit_limit.fiscal_year_id)

    policy = queryset.first()
    if policy:
        return policy

    if credit_limit:
        fallback = CreditPolicy.objects.filter(
            is_active=True,
            is_default=True,
            branch__isnull=True,
            fiscal_year__isnull=True,
        ).first()
        if fallback:
            return fallback
    return None


def synchronize_credit_limit(credit_limit: CreditLimit) -> CreditLimit:
    totals = CreditTransaction.objects.filter(party=credit_limit.party).aggregate(
        debit_total=Coalesce(Sum("debit"), ZERO),
        credit_total=Coalesce(Sum("credit"), ZERO),
    )
    used_credit = max(to_decimal(totals["debit_total"]) - to_decimal(totals["credit_total"]), ZERO)
    CreditLimit.objects.filter(pk=credit_limit.pk).update(used_credit=used_credit)
    credit_limit.used_credit = used_credit
    return credit_limit


def evaluate_credit_availability(party, requested_amount, *, branch_id=None, fiscal_year_id=None):
    credit_limit = get_or_create_credit_limit(party, branch_id=branch_id, fiscal_year_id=fiscal_year_id)
    synchronize_credit_limit(credit_limit)
    policy = get_applicable_credit_policy(credit_limit)
    requested_amount = to_decimal(requested_amount)
    base_limit = to_decimal(credit_limit.credit_limit)
    effective_limit = base_limit

    if policy and policy.allow_over_limit:
        effective_limit += (base_limit * to_decimal(policy.over_limit_percentage) / HUNDRED).quantize(Decimal("0.01"))

    available = effective_limit - to_decimal(credit_limit.used_credit)
    is_allowed = requested_amount <= available
    should_block = bool(policy and policy.block_sales and not is_allowed)

    return {
        "credit_limit": credit_limit,
        "policy": policy,
        "base_limit": base_limit,
        "effective_limit": effective_limit,
        "used_credit": to_decimal(credit_limit.used_credit),
        "available_credit": available,
        "requested_amount": requested_amount,
        "is_allowed": is_allowed,
        "should_block_sales": should_block,
    }


@transaction.atomic
def record_credit_transaction(
    *,
    party,
    document_type,
    debit=ZERO,
    credit=ZERO,
    document=None,
    document_id="",
    transaction_date=None,
    branch_id=None,
    fiscal_year_id=None,
    remarks="",
    is_system_generated=True,
):
    credit_limit = get_or_create_credit_limit(party, branch_id=branch_id, fiscal_year_id=fiscal_year_id)
    locked_limit = CreditLimit.objects.select_for_update().get(pk=credit_limit.pk)
    synchronize_credit_limit(locked_limit)

    debit_amount = to_decimal(debit)
    credit_amount = to_decimal(credit)
    current_balance = to_decimal(locked_limit.used_credit)
    next_balance = current_balance + debit_amount - credit_amount

    if next_balance < ZERO:
        raise ValidationError({"credit": "Credit transaction would reduce used credit below zero."})

    content_type = None
    object_id = None
    resolved_document_id = (document_id or "").strip()
    if document is not None:
        content_type = ContentType.objects.get_for_model(document, for_concrete_model=False)
        object_id = document.pk
        if not resolved_document_id:
            resolved_document_id = str(getattr(document, "document_number", "") or getattr(document, "payment_no", "") or document.pk)

    transaction_obj = CreditTransaction.objects.create(
        party=party,
        branch_id=locked_limit.branch_id,
        fiscal_year_id=locked_limit.fiscal_year_id,
        document_type=document_type,
        document_id=resolved_document_id,
        content_type=content_type,
        object_id=object_id,
        transaction_date=transaction_date,
        debit=debit_amount,
        credit=credit_amount,
        balance_after=next_balance,
        is_system_generated=is_system_generated,
        remarks=(remarks or "").strip(),
    )

    CreditLimit.objects.filter(pk=locked_limit.pk).update(used_credit=next_balance)
    locked_limit.used_credit = next_balance
    return transaction_obj

