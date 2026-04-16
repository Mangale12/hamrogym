from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, Iterable, List

from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce

from ..models import ChartOfAccount, LedgerPosting


ZERO = Decimal("0.00")
DECIMAL_OUTPUT = DecimalField(max_digits=18, decimal_places=2)
NORMAL_BALANCE_BY_TYPE = {
    "asset": "debit",
    "liability": "credit",
    "equity": "credit",
    "income": "credit",
    "expense": "debit",
}


def quantize_amount(value: Decimal | None) -> Decimal:
    return (value or ZERO).quantize(Decimal("0.01"))


def signed_balance(account_type: str, debit_amount: Decimal, credit_amount: Decimal) -> Decimal:
    normal_side = NORMAL_BALANCE_BY_TYPE.get(account_type, "debit")
    if normal_side == "credit":
        return quantize_amount(credit_amount - debit_amount)
    return quantize_amount(debit_amount - credit_amount)


def scope_account_queryset(queryset, *, organization=None, branch=None, fiscal_year=None):
    if organization:
        queryset = queryset.filter(Q(organization=organization) | Q(organization__isnull=True))
    if branch:
        queryset = queryset.filter(Q(branch=branch) | Q(branch__isnull=True))
    if fiscal_year:
        queryset = queryset.filter(Q(fiscal_year=fiscal_year) | Q(fiscal_year__isnull=True))
    return queryset


def iter_missing_ancestors(account_ids: Iterable[int], existing_ids: set[int]) -> List[ChartOfAccount]:
    pending_ids = {account_id for account_id in account_ids if account_id and account_id not in existing_ids}
    collected: Dict[int, ChartOfAccount] = {}

    while pending_ids:
        batch = list(
            ChartOfAccount.objects.filter(pk__in=pending_ids)
            .select_related("parent")
            .order_by("code", "sort_order", "id")
        )
        pending_ids = set()
        for account in batch:
            if account.pk in collected:
                continue
            collected[account.pk] = account
            if account.parent_id and account.parent_id not in existing_ids and account.parent_id not in collected:
                pending_ids.add(account.parent_id)

    return list(collected.values())


def build_section_rows(
    root_accounts: Iterable[ChartOfAccount],
    *,
    balance_map: Dict[int, Decimal],
    children_map: Dict[int | None, List[ChartOfAccount]],
    show_zero_balances: bool,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def visit(account: ChartOfAccount) -> bool:
        account_balance = quantize_amount(balance_map.get(account.pk))
        child_rows_before = len(rows)
        visible_child_found = False

        for child in children_map.get(account.pk, []):
            visible_child_found = visit(child) or visible_child_found

        has_value = account_balance != ZERO
        is_visible = show_zero_balances or has_value or visible_child_found
        if not is_visible:
            del rows[child_rows_before:]
            return False

        row = {
            "id": account.pk,
            "code": account.code or "",
            "name": account.name,
            "account_type": account.account_type,
            "level": account.report_level or 1,
            "depth": max((account.report_level or 1) - 1, 0),
            "indent_px": max((account.report_level or 1) - 1, 0) * 18,
            "is_group": not account.is_ledger,
            "is_ledger": bool(account.is_ledger),
            "amount": account_balance,
            "is_negative": account_balance < ZERO,
        }
        rows.insert(child_rows_before, row)
        return True

    for root_account in root_accounts:
        visit(root_account)

    return rows


def flatten_export_rows(section_label: str, rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    export_rows = []
    for row in rows:
        export_rows.append(
            {
                "section": section_label,
                "code": row.get("code", ""),
                "account": row.get("name", ""),
                "level": row.get("level", 1),
                "account_kind": "Group" if row.get("is_group") else "Ledger",
                "amount": row.get("amount", ZERO),
            }
        )
    return export_rows


def build_account_balance_snapshot(
    *,
    report_type: str,
    account_types: Iterable[str],
    organization=None,
    branch=None,
    fiscal_year=None,
    date_from=None,
    date_to=None,
) -> Dict[str, Any]:
    account_type_list = list(account_types or [])

    posting_queryset = LedgerPosting.objects.select_related("account", "journal_entry")
    if account_type_list:
        posting_queryset = posting_queryset.filter(account__account_type__in=account_type_list)
    if organization:
        posting_queryset = posting_queryset.filter(journal_entry__organization=organization)
    if branch:
        posting_queryset = posting_queryset.filter(journal_entry__branch=branch)
    if fiscal_year:
        posting_queryset = posting_queryset.filter(journal_entry__fiscal_year=fiscal_year)
    if date_from:
        posting_queryset = posting_queryset.filter(posting_date__gte=date_from)
    if date_to:
        posting_queryset = posting_queryset.filter(posting_date__lte=date_to)

    posting_totals = list(
        posting_queryset.values("account_id", "account__account_type").annotate(
            total_debit=Coalesce(Sum("debit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
            total_credit=Coalesce(Sum("credit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
        )
    )

    direct_balance_map: Dict[int, Decimal] = {}
    account_ids = set()
    totals_by_type = {account_type: ZERO for account_type in account_type_list}

    for item in posting_totals:
        account_id = item.get("account_id")
        account_type = item.get("account__account_type") or ""
        balance = signed_balance(account_type, item["total_debit"], item["total_credit"])
        direct_balance_map[account_id] = balance
        account_ids.add(account_id)
        if account_type in totals_by_type:
            totals_by_type[account_type] += balance

    account_queryset = ChartOfAccount.objects.filter(report_type=report_type).select_related("parent")
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

    children_map: Dict[int | None, List[ChartOfAccount]] = defaultdict(list)
    for account in ordered_accounts:
        children_map[account.parent_id].append(account)

    rolled_balance_map: Dict[int, Decimal] = {}

    def rollup(account: ChartOfAccount) -> Decimal:
        if account.pk in rolled_balance_map:
            return rolled_balance_map[account.pk]

        total = quantize_amount(direct_balance_map.get(account.pk))
        for child in children_map.get(account.pk, []):
            total += rollup(child)
        rolled_balance_map[account.pk] = quantize_amount(total)
        return rolled_balance_map[account.pk]

    for account in ordered_accounts:
        rollup(account)

    return {
        "ordered_accounts": ordered_accounts,
        "children_map": children_map,
        "direct_balance_map": direct_balance_map,
        "rolled_balance_map": rolled_balance_map,
        "totals_by_type": {key: quantize_amount(value) for key, value in totals_by_type.items()},
    }
