from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from ..models import ChartOfAccount, LedgerPosting
from .reporting import (
    NORMAL_BALANCE_BY_TYPE,
    ZERO,
    iter_missing_ancestors,
    quantize_amount,
    scope_account_queryset,
    signed_balance,
)


DECIMAL_OUTPUT = DecimalField(max_digits=18, decimal_places=2)
ACCOUNT_TYPE_LABELS = {
    "asset": "Asset",
    "liability": "Liability",
    "equity": "Equity",
    "income": "Income",
    "expense": "Expense",
}


def split_balance_columns(account_type: str, amount) -> tuple:
    normalized = quantize_amount(amount)
    normal_side = NORMAL_BALANCE_BY_TYPE.get(account_type, "debit")

    if normalized == ZERO:
        return ZERO, ZERO

    if normal_side == "debit":
        return (normalized, ZERO) if normalized >= ZERO else (ZERO, abs(normalized))
    return (ZERO, normalized) if normalized >= ZERO else (abs(normalized), ZERO)


def _posting_scope(*, organization=None, branch=None, fiscal_year=None):
    queryset = LedgerPosting.objects.select_related("account", "journal_entry")
    if organization:
        queryset = queryset.filter(journal_entry__organization=organization)
    if branch:
        queryset = queryset.filter(journal_entry__branch=branch)
    if fiscal_year:
        queryset = queryset.filter(journal_entry__fiscal_year=fiscal_year)
    return queryset


def _sum_columns(base: Dict[str, Any], increment: Dict[str, Any]) -> Dict[str, Any]:
    for key in (
        "opening_debit",
        "opening_credit",
        "period_debit",
        "period_credit",
        "closing_debit",
        "closing_credit",
        "ledger_count",
    ):
        base[key] = quantize_amount(base[key] + increment[key]) if key != "ledger_count" else base[key] + increment[key]
    return base


def build_trial_balance_report(
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

    posting_queryset = _posting_scope(
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    )

    opening_totals = list(
        posting_queryset.filter(posting_date__lt=start_date)
        .values("account_id", "account__account_type")
        .annotate(
            total_debit=Coalesce(Sum("debit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
            total_credit=Coalesce(Sum("credit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
        )
    )
    period_totals = list(
        posting_queryset.filter(posting_date__gte=start_date, posting_date__lte=end_date)
        .values("account_id", "account__account_type")
        .annotate(
            total_debit=Coalesce(Sum("debit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
            total_credit=Coalesce(Sum("credit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
        )
    )

    opening_balance_map: Dict[int, Any] = {}
    period_debit_map: Dict[int, Any] = {}
    period_credit_map: Dict[int, Any] = {}
    account_ids = set()

    for item in opening_totals:
        account_id = item["account_id"]
        opening_balance_map[account_id] = signed_balance(
            item.get("account__account_type") or "",
            item["total_debit"],
            item["total_credit"],
        )
        account_ids.add(account_id)

    for item in period_totals:
        account_id = item["account_id"]
        period_debit_map[account_id] = quantize_amount(item["total_debit"])
        period_credit_map[account_id] = quantize_amount(item["total_credit"])
        account_ids.add(account_id)

    account_queryset = ChartOfAccount.objects.select_related("parent")
    scoped_accounts = list(
        scope_account_queryset(
            account_queryset,
            organization=organization,
            branch=branch,
            fiscal_year=fiscal_year,
        ).order_by("code", "sort_order", "id")
    )
    accounts_by_id = {account.pk: account for account in scoped_accounts}

    missing_accounts = iter_missing_ancestors(account_ids, set(accounts_by_id))
    for account in missing_accounts:
        accounts_by_id.setdefault(account.pk, account)

    ordered_accounts = sorted(
        accounts_by_id.values(),
        key=lambda account: (account.code or "", account.sort_order, account.id),
    )

    children_map = defaultdict(list)
    for account in ordered_accounts:
        children_map[account.parent_id].append(account)

    def visit(account: ChartOfAccount) -> Dict[str, Any] | None:
        totals = {
            "opening_debit": ZERO,
            "opening_credit": ZERO,
            "period_debit": ZERO,
            "period_credit": ZERO,
            "closing_debit": ZERO,
            "closing_credit": ZERO,
            "ledger_count": 0,
        }
        child_rows: List[Dict[str, Any]] = []

        for child in children_map.get(account.pk, []):
            child_result = visit(child)
            if not child_result:
                continue
            child_rows.extend(child_result["rows"])
            totals = _sum_columns(totals, child_result["totals"])

        if account.is_ledger:
            opening_balance = quantize_amount(opening_balance_map.get(account.pk))
            period_debit = quantize_amount(period_debit_map.get(account.pk))
            period_credit = quantize_amount(period_credit_map.get(account.pk))
            movement_balance = signed_balance(account.account_type, period_debit, period_credit)
            closing_balance = quantize_amount(opening_balance + movement_balance)
            opening_debit, opening_credit = split_balance_columns(account.account_type, opening_balance)
            closing_debit, closing_credit = split_balance_columns(account.account_type, closing_balance)

            totals = {
                "opening_debit": opening_debit,
                "opening_credit": opening_credit,
                "period_debit": period_debit,
                "period_credit": period_credit,
                "closing_debit": closing_debit,
                "closing_credit": closing_credit,
                "ledger_count": 1,
            }

        is_visible = show_zero_balances or any(
            totals[key] != ZERO
            for key in (
                "opening_debit",
                "opening_credit",
                "period_debit",
                "period_credit",
                "closing_debit",
                "closing_credit",
            )
        ) or bool(child_rows)
        if not is_visible:
            return None

        row = {
            "id": account.pk,
            "code": account.code or "",
            "name": account.name,
            "full_path": account.full_path,
            "account_type": account.account_type,
            "account_type_label": ACCOUNT_TYPE_LABELS.get(account.account_type, account.account_type.title()),
            "level": account.report_level or 1,
            "indent_px": max((account.report_level or 1) - 1, 0) * 18,
            "is_group": not account.is_ledger,
            "is_ledger": bool(account.is_ledger),
            "opening_debit": totals["opening_debit"],
            "opening_credit": totals["opening_credit"],
            "period_debit": totals["period_debit"],
            "period_credit": totals["period_credit"],
            "closing_debit": totals["closing_debit"],
            "closing_credit": totals["closing_credit"],
            "ledger_count": totals["ledger_count"],
        }

        return {
            "rows": [row, *child_rows],
            "totals": totals,
        }

    rows: List[Dict[str, Any]] = []
    report_totals = {
        "opening_debit": ZERO,
        "opening_credit": ZERO,
        "period_debit": ZERO,
        "period_credit": ZERO,
        "closing_debit": ZERO,
        "closing_credit": ZERO,
        "ledger_count": 0,
    }

    for root_account in children_map.get(None, []):
        result = visit(root_account)
        if not result:
            continue
        rows.extend(result["rows"])
        report_totals = _sum_columns(report_totals, result["totals"])

    export_rows = [
        {
            "code": row["code"],
            "account": row["full_path"],
            "account_type": row["account_type_label"],
            "level": row["level"],
            "account_kind": "Group" if row["is_group"] else "Ledger",
            "opening_debit": row["opening_debit"],
            "opening_credit": row["opening_credit"],
            "period_debit": row["period_debit"],
            "period_credit": row["period_credit"],
            "closing_debit": row["closing_debit"],
            "closing_credit": row["closing_credit"],
        }
        for row in rows
    ]

    opening_difference = quantize_amount(report_totals["opening_debit"] - report_totals["opening_credit"])
    period_difference = quantize_amount(report_totals["period_debit"] - report_totals["period_credit"])
    closing_difference = quantize_amount(report_totals["closing_debit"] - report_totals["closing_credit"])

    export_rows.append(
        {
            "code": "",
            "account": "Grand Total",
            "account_type": "Summary",
            "level": 0,
            "account_kind": "Summary",
            "opening_debit": report_totals["opening_debit"],
            "opening_credit": report_totals["opening_credit"],
            "period_debit": report_totals["period_debit"],
            "period_credit": report_totals["period_credit"],
            "closing_debit": report_totals["closing_debit"],
            "closing_credit": report_totals["closing_credit"],
        }
    )

    return {
        "report_title": "Trial Balance",
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
            "accounts": report_totals["ledger_count"],
            "opening_debit": report_totals["opening_debit"],
            "opening_credit": report_totals["opening_credit"],
            "period_debit": report_totals["period_debit"],
            "period_credit": report_totals["period_credit"],
            "closing_debit": report_totals["closing_debit"],
            "closing_credit": report_totals["closing_credit"],
            "opening_difference": opening_difference,
            "period_difference": period_difference,
            "closing_difference": closing_difference,
            "is_balanced": opening_difference == ZERO and period_difference == ZERO and closing_difference == ZERO,
        },
    }
