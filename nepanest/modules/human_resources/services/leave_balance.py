from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from nepanest.modules.leave.models import LeaveAccrual, LeaveBalance, LeaveLedger


ZERO = Decimal("0.00")


def _to_decimal(value) -> Decimal:
    if value is None:
        return ZERO
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _leave_year(for_date) -> int:
    return int(for_date.year)


@transaction.atomic
def get_or_create_leave_balance(*, employee, leave_type, year: int) -> LeaveBalance:
    balance, _created = LeaveBalance.objects.select_for_update().get_or_create(
        employee=employee,
        leave_type=leave_type,
        year=year,
        defaults={
            "opening_balance": ZERO,
            "accrued": ZERO,
            "used": ZERO,
            "encashed": ZERO,
            "balance": ZERO,
        },
    )
    return balance


@transaction.atomic
def sync_leave_balance(*, employee, leave_type, year: int) -> LeaveBalance:
    balance = get_or_create_leave_balance(employee=employee, leave_type=leave_type, year=year)
    ledger_rows = LeaveLedger.objects.filter(employee=employee, leave_type=leave_type, year=year)

    opening_balance = _sum_ledger_days(ledger_rows.filter(change_type="opening"))
    accrued = _sum_ledger_days(
        ledger_rows.filter(change_type__in=["accrual", "carry_forward", "compoff_earned", "adjustment"])
    )
    used = _sum_ledger_days(
        ledger_rows.filter(change_type__in=["leave_approved", "compoff_used", "leave_cancelled"])
    )
    encashed = _sum_ledger_days(ledger_rows.filter(change_type="encashment"))

    effective_used = abs(_negative_only(used))
    effective_accrued = accrued + _positive_only(used)
    current_balance = opening_balance + effective_accrued - effective_used - encashed

    balance.opening_balance = opening_balance
    balance.accrued = effective_accrued
    balance.used = effective_used
    balance.encashed = encashed
    balance.balance = current_balance
    balance.save(
        update_fields=[
            "opening_balance",
            "accrued",
            "used",
            "encashed",
            "balance",
            "updated_at",
        ]
    )
    return balance


def _sum_ledger_days(queryset) -> Decimal:
    total = queryset.aggregate(total=Sum("days")).get("total")
    return _to_decimal(total or ZERO)


def _positive_only(value: Decimal) -> Decimal:
    return value if value > ZERO else ZERO


def _negative_only(value: Decimal) -> Decimal:
    return value if value < ZERO else ZERO


@transaction.atomic
def create_leave_ledger_entry(
    *,
    employee,
    leave_type,
    change_type: str,
    days,
    effective_date,
    reference=None,
    remarks: str = "",
) -> LeaveLedger:
    year = _leave_year(effective_date)
    balance = get_or_create_leave_balance(employee=employee, leave_type=leave_type, year=year)
    days_decimal = _to_decimal(days)
    balance_after = _to_decimal(balance.balance + days_decimal)
    ledger = LeaveLedger.objects.create(
        employee=employee,
        leave_type=leave_type,
        year=year,
        change_type=change_type,
        days=days_decimal,
        reference_type=reference.__class__.__name__ if reference is not None else "",
        reference_id=getattr(reference, "pk", None),
        balance_after=balance_after,
        remarks=(remarks or "").strip(),
    )
    sync_leave_balance(employee=employee, leave_type=leave_type, year=year)
    return ledger


@transaction.atomic
def apply_leave_accrual(
    *,
    employee,
    leave_type,
    accrual_date,
    days_added,
    policy=None,
    remarks: str = "",
):
    days_decimal = _to_decimal(days_added)
    accrual = LeaveAccrual.objects.create(
        employee=employee,
        leave_type=leave_type,
        policy=policy,
        accrual_date=accrual_date,
        days_added=days_decimal,
        remarks=(remarks or "").strip(),
    )
    create_leave_ledger_entry(
        employee=employee,
        leave_type=leave_type,
        change_type="accrual",
        days=days_decimal,
        effective_date=accrual_date,
        reference=accrual,
        remarks=remarks,
    )
    return accrual


@transaction.atomic
def consume_leave_balance(*, leave_request, remarks: str = "") -> LeaveLedger:
    return create_leave_ledger_entry(
        employee=leave_request.employee,
        leave_type=leave_request.leave_type,
        change_type="leave_approved",
        days=_to_decimal(leave_request.total_days) * Decimal("-1"),
        effective_date=leave_request.start_date,
        reference=leave_request,
        remarks=remarks or f"Leave approved for {leave_request.start_date} to {leave_request.end_date}",
    )


@transaction.atomic
def reverse_leave_balance(*, leave_request, remarks: str = "") -> LeaveLedger:
    return create_leave_ledger_entry(
        employee=leave_request.employee,
        leave_type=leave_request.leave_type,
        change_type="leave_cancelled",
        days=_to_decimal(leave_request.total_days),
        effective_date=leave_request.start_date,
        reference=leave_request,
        remarks=remarks or f"Leave reversed for {leave_request.start_date} to {leave_request.end_date}",
    )


def get_available_leave_balance(*, employee, leave_type, year: int) -> Decimal:
    balance = sync_leave_balance(employee=employee, leave_type=leave_type, year=year)
    return _to_decimal(balance.balance)
