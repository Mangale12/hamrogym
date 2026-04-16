from __future__ import annotations

import re
from typing import Any, Dict, List

from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from ..models import ChartOfAccount, LedgerPosting
from .reporting import ZERO, quantize_amount, scope_account_queryset, signed_balance


DECIMAL_OUTPUT = DecimalField(max_digits=18, decimal_places=2)
NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


def _posting_scope(*, organization=None, branch=None, fiscal_year=None):
    queryset = LedgerPosting.objects.select_related("account", "journal_entry")
    if organization:
        queryset = queryset.filter(journal_entry__organization=organization)
    if branch:
        queryset = queryset.filter(journal_entry__branch=branch)
    if fiscal_year:
        queryset = queryset.filter(journal_entry__fiscal_year=fiscal_year)
    return queryset


def _normalize_asset_key(name: str) -> str:
    value = (name or "").lower()
    for token in (
        "accumulated depreciation",
        "depreciation expense",
        "depreciation",
        "expense",
    ):
        value = value.replace(token, " ")
    value = NORMALIZE_RE.sub(" ", value)
    return " ".join(value.split()).strip()


def _label_for_key(key: str) -> str:
    return " ".join(part.capitalize() for part in (key or "").split()) or "Unclassified"


def _account_label(account: ChartOfAccount | None) -> str:
    if not account:
        return "-"
    return f"{account.code or 'AUTO'} - {account.name}"


def _account_metrics(
    account: ChartOfAccount | None,
    *,
    date_from,
    date_to,
    organization=None,
    branch=None,
    fiscal_year=None,
) -> Dict[str, Any]:
    if not account:
        return {
            "opening_balance": ZERO,
            "period_debit": ZERO,
            "period_credit": ZERO,
            "period_balance": ZERO,
            "closing_balance": ZERO,
        }

    queryset = _posting_scope(
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    ).filter(account=account)

    opening = queryset.filter(posting_date__lt=date_from).aggregate(
        total_debit=Coalesce(Sum("debit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
        total_credit=Coalesce(Sum("credit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
    )
    period = queryset.filter(posting_date__gte=date_from, posting_date__lte=date_to).aggregate(
        total_debit=Coalesce(Sum("debit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
        total_credit=Coalesce(Sum("credit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
    )

    opening_balance = signed_balance(account.account_type, opening["total_debit"], opening["total_credit"])
    period_debit = quantize_amount(period["total_debit"])
    period_credit = quantize_amount(period["total_credit"])
    period_balance = signed_balance(account.account_type, period_debit, period_credit)
    closing_balance = quantize_amount(opening_balance + period_balance)

    return {
        "opening_balance": quantize_amount(opening_balance),
        "period_debit": period_debit,
        "period_credit": period_credit,
        "period_balance": quantize_amount(period_balance),
        "closing_balance": quantize_amount(closing_balance),
    }


def build_depreciation_effect_report(
    *,
    organization=None,
    branch=None,
    fiscal_year=None,
    date_from=None,
    date_to=None,
    show_zero_balances: bool = False,
) -> Dict[str, Any]:
    today = timezone.localdate()
    start_date = date_from or (fiscal_year.start_date if fiscal_year else None) or today.replace(month=1, day=1)
    end_date = date_to or today

    if fiscal_year:
        if start_date < fiscal_year.start_date:
            start_date = fiscal_year.start_date
        if end_date > fiscal_year.end_date:
            end_date = fiscal_year.end_date

    accounts = list(
        scope_account_queryset(
            ChartOfAccount.objects.filter(is_ledger=True, is_active=True).select_related("parent"),
            organization=organization,
            branch=branch,
            fiscal_year=fiscal_year,
        ).order_by("code", "sort_order", "id")
    )

    fixed_asset_accounts: Dict[str, ChartOfAccount] = {}
    accumulated_accounts: Dict[str, ChartOfAccount] = {}
    expense_accounts: Dict[str, ChartOfAccount] = {}

    for account in accounts:
        key = _normalize_asset_key(account.name)
        if not key:
            continue

        if account.is_depreciation and account.account_type == "expense":
            expense_accounts[key] = account
            continue

        if account.is_depreciation and account.account_type == "asset":
            accumulated_accounts[key] = account
            continue

        if account.account_type == "asset" and not account.is_depreciation:
            fixed_asset_accounts.setdefault(key, account)

    all_keys = sorted(set(fixed_asset_accounts) | set(accumulated_accounts) | set(expense_accounts))

    rows: List[Dict[str, Any]] = []
    total_opening_cost = ZERO
    total_additions = ZERO
    total_disposals = ZERO
    total_closing_cost = ZERO
    total_opening_accumulated = ZERO
    total_period_expense = ZERO
    total_period_accumulated = ZERO
    total_closing_accumulated = ZERO
    total_opening_nbv = ZERO
    total_closing_nbv = ZERO

    # Each row shows the complete accounting effect of depreciation:
    # fixed asset cost, current-period depreciation expense, accumulated
    # depreciation movement, and net book value before and after the period.
    for key in all_keys:
        asset_account = fixed_asset_accounts.get(key)
        accumulated_account = accumulated_accounts.get(key)
        expense_account = expense_accounts.get(key)

        asset_metrics = _account_metrics(
            asset_account,
            date_from=start_date,
            date_to=end_date,
            organization=organization,
            branch=branch,
            fiscal_year=fiscal_year,
        )
        accumulated_metrics = _account_metrics(
            accumulated_account,
            date_from=start_date,
            date_to=end_date,
            organization=organization,
            branch=branch,
            fiscal_year=fiscal_year,
        )
        expense_metrics = _account_metrics(
            expense_account,
            date_from=start_date,
            date_to=end_date,
            organization=organization,
            branch=branch,
            fiscal_year=fiscal_year,
        )

        opening_cost = quantize_amount(max(asset_metrics["opening_balance"], ZERO))
        asset_change = asset_metrics["period_balance"]
        additions = quantize_amount(asset_change if asset_change > ZERO else ZERO)
        disposals = quantize_amount(abs(asset_change) if asset_change < ZERO else ZERO)
        closing_cost = quantize_amount(max(asset_metrics["closing_balance"], ZERO))

        opening_accumulated = quantize_amount(abs(accumulated_metrics["opening_balance"]))
        period_accumulated_effect = quantize_amount(
            accumulated_metrics["period_credit"] - accumulated_metrics["period_debit"]
        )
        closing_accumulated = quantize_amount(abs(accumulated_metrics["closing_balance"]))
        period_expense = quantize_amount(expense_metrics["period_balance"])

        opening_nbv = quantize_amount(opening_cost - opening_accumulated)
        closing_nbv = quantize_amount(closing_cost - closing_accumulated)
        reconciliation_gap = quantize_amount(period_expense - period_accumulated_effect)

        if not show_zero_balances and not any(
            [
                opening_cost,
                additions,
                disposals,
                closing_cost,
                opening_accumulated,
                period_accumulated_effect,
                closing_accumulated,
                period_expense,
            ]
        ):
            continue

        row = {
            "asset_class": _label_for_key(key),
            "fixed_asset_account": _account_label(asset_account),
            "accumulated_account": _account_label(accumulated_account),
            "expense_account": _account_label(expense_account),
            "opening_cost": opening_cost,
            "additions": additions,
            "disposals": disposals,
            "closing_cost": closing_cost,
            "opening_accumulated": opening_accumulated,
            "period_expense": period_expense,
            "period_accumulated_effect": period_accumulated_effect,
            "closing_accumulated": closing_accumulated,
            "opening_nbv": opening_nbv,
            "closing_nbv": closing_nbv,
            "reconciliation_gap": reconciliation_gap,
        }
        rows.append(row)

        total_opening_cost += opening_cost
        total_additions += additions
        total_disposals += disposals
        total_closing_cost += closing_cost
        total_opening_accumulated += opening_accumulated
        total_period_expense += period_expense
        total_period_accumulated += period_accumulated_effect
        total_closing_accumulated += closing_accumulated
        total_opening_nbv += opening_nbv
        total_closing_nbv += closing_nbv

    total_opening_cost = quantize_amount(total_opening_cost)
    total_additions = quantize_amount(total_additions)
    total_disposals = quantize_amount(total_disposals)
    total_closing_cost = quantize_amount(total_closing_cost)
    total_opening_accumulated = quantize_amount(total_opening_accumulated)
    total_period_expense = quantize_amount(total_period_expense)
    total_period_accumulated = quantize_amount(total_period_accumulated)
    total_closing_accumulated = quantize_amount(total_closing_accumulated)
    total_opening_nbv = quantize_amount(total_opening_nbv)
    total_closing_nbv = quantize_amount(total_closing_nbv)
    total_reconciliation_gap = quantize_amount(total_period_expense - total_period_accumulated)

    export_rows = [
        {
            "asset_class": row["asset_class"],
            "fixed_asset_account": row["fixed_asset_account"],
            "accumulated_account": row["accumulated_account"],
            "expense_account": row["expense_account"],
            "opening_cost": row["opening_cost"],
            "additions": row["additions"],
            "disposals": row["disposals"],
            "closing_cost": row["closing_cost"],
            "opening_accumulated": row["opening_accumulated"],
            "period_expense": row["period_expense"],
            "period_accumulated_effect": row["period_accumulated_effect"],
            "closing_accumulated": row["closing_accumulated"],
            "opening_nbv": row["opening_nbv"],
            "closing_nbv": row["closing_nbv"],
            "reconciliation_gap": row["reconciliation_gap"],
        }
        for row in rows
    ]

    return {
        "report_title": "Depreciation Effect Report",
        "generated_at": timezone.localtime(),
        "organization": organization,
        "branch": branch,
        "fiscal_year": fiscal_year,
        "date_from": start_date,
        "date_to": end_date,
        "show_zero_balances": show_zero_balances,
        "rows": export_rows,
        "report_rows": rows,
        "summary": {
            "classes": len(rows),
            "opening_cost": total_opening_cost,
            "additions": total_additions,
            "disposals": total_disposals,
            "closing_cost": total_closing_cost,
            "opening_accumulated": total_opening_accumulated,
            "period_expense": total_period_expense,
            "period_accumulated_effect": total_period_accumulated,
            "closing_accumulated": total_closing_accumulated,
            "opening_nbv": total_opening_nbv,
            "closing_nbv": total_closing_nbv,
            "reconciliation_gap": total_reconciliation_gap,
            "is_balanced": total_reconciliation_gap == ZERO,
        },
    }
