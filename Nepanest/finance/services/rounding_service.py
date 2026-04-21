from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP

from django.db.models import Q

from ..models import (
    Rounding,
    RoundingApplicationScope,
    RoundingDocumentType,
    RoundingMethod,
    RoundingRule,
)


ZERO = Decimal("0.00")
ROUNDING_MAP = {
    RoundingMethod.HALF_UP: ROUND_HALF_UP,
    RoundingMethod.HALF_DOWN: ROUND_HALF_DOWN,
    RoundingMethod.HALF_EVEN: ROUND_HALF_EVEN,
    RoundingMethod.UP: ROUND_UP,
    RoundingMethod.DOWN: ROUND_DOWN,
    RoundingMethod.CEILING: ROUND_CEILING,
    RoundingMethod.FLOOR: ROUND_FLOOR,
}


def to_decimal(value) -> Decimal:
    if value in (None, ""):
        return ZERO
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return ZERO


def apply_rounding(value, rounding: Rounding) -> Decimal:
    amount = to_decimal(value)
    increment = to_decimal(rounding.increment)
    if increment <= 0:
        return amount

    normalized = amount / increment
    rounded_units = normalized.quantize(Decimal("1"), rounding=ROUNDING_MAP[rounding.rounding_method])
    rounded_amount = rounded_units * increment

    scale = Decimal("1").scaleb(-int(rounding.precision or 0))
    return rounded_amount.quantize(scale, rounding=ROUNDING_MAP[rounding.rounding_method])


def resolve_rounding_rule(
    *,
    application_scope: str = RoundingApplicationScope.BOTH,
    document_type: str = RoundingDocumentType.ALL,
    party_type_id=None,
    currency_id=None,
    payment_method_id=None,
    amount=None,
    branch_id=None,
    fiscal_year_id=None,
):
    resolved_amount = to_decimal(amount)
    queryset = (
        RoundingRule.objects.select_related("rounding")
        .filter(is_active=True, rounding__is_active=True)
        .filter(Q(application_scope=application_scope) | Q(application_scope=RoundingApplicationScope.BOTH))
        .filter(Q(document_type=document_type) | Q(document_type=RoundingDocumentType.ALL))
        .filter(Q(branch_id=branch_id) | Q(branch__isnull=True))
        .filter(Q(fiscal_year_id=fiscal_year_id) | Q(fiscal_year__isnull=True))
    )

    if party_type_id:
        queryset = queryset.filter(Q(party_type_id=party_type_id) | Q(party_type__isnull=True))
    if currency_id:
        queryset = queryset.filter(Q(currency_id=currency_id) | Q(currency__isnull=True))
    if payment_method_id:
        queryset = queryset.filter(Q(payment_method_id=payment_method_id) | Q(payment_method__isnull=True))

    queryset = queryset.filter(Q(min_amount__isnull=True) | Q(min_amount__lte=resolved_amount))
    queryset = queryset.filter(Q(max_amount__isnull=True) | Q(max_amount__gte=resolved_amount))
    return queryset.order_by("priority", "id").first()


def resolve_rounding(*args, **kwargs):
    rule = resolve_rounding_rule(*args, **kwargs)
    return rule.rounding if rule else None

