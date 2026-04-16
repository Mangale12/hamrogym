from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List

from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from ..models import ChartOfAccount, LedgerPosting
from .books import is_special_book_account
from .reporting import ZERO, quantize_amount, scope_account_queryset, signed_balance


DECIMAL_OUTPUT = DecimalField(max_digits=18, decimal_places=2)

SECTION_META = {
    "operating": {"label": "Operating Activities"},
    "investing": {"label": "Investing Activities"},
    "financing": {"label": "Financing Activities"},
}

CASH_EQUIVALENT_EXTRA_KEYWORDS = (
    "wallet",
    "mobile wallet",
    "esewa",
    "khalti",
    "fonepay",
)
CURRENT_ASSET_KEYWORDS = (
    "current asset",
    "inventory",
    "stock",
    "receivable",
    "debtor",
    "advance",
    "prepaid",
    "vat receivable",
    "tax receivable",
    "tds receivable",
    "input vat",
    "input tax",
    "short term",
)
INVESTING_ASSET_KEYWORDS = (
    "fixed asset",
    "non current asset",
    "non-current asset",
    "property",
    "plant",
    "equipment",
    "ppe",
    "furniture",
    "fixture",
    "vehicle",
    "building",
    "land",
    "machinery",
    "computer",
    "office equipment",
    "intangible",
    "goodwill",
    "capital work",
    "construction",
    "cwip",
    "investment",
    "security deposit",
    "fixed deposit",
    "fd account",
)
FINANCING_LIABILITY_KEYWORDS = (
    "loan",
    "borrowing",
    "term loan",
    "bank loan",
    "overdraft",
    "od account",
    "lease liability",
    "hire purchase",
    "mortgage",
    "debenture",
    "finance",
)


def _account_text(account: ChartOfAccount) -> str:
    return " ".join(
        [
            str(account.code or ""),
            str(account.name or ""),
            str(account.full_path or ""),
        ]
    ).lower()


def is_cash_equivalent_account(account: ChartOfAccount) -> bool:
    if not account or not account.is_ledger or account.account_type != "asset":
        return False

    if is_special_book_account(account, "cash") or is_special_book_account(account, "bank"):
        return True

    haystack = _account_text(account)
    return any(keyword in haystack for keyword in CASH_EQUIVALENT_EXTRA_KEYWORDS)


def _classify_counterparty_account(account: ChartOfAccount) -> str:
    if not account:
        return "operating"

    if account.account_type in {"income", "expense"}:
        return "operating"

    if account.account_type == "equity":
        return "financing"

    haystack = _account_text(account)

    if account.account_type == "liability":
        if any(keyword in haystack for keyword in FINANCING_LIABILITY_KEYWORDS):
            return "financing"
        return "operating"

    if account.account_type == "asset":
        if is_cash_equivalent_account(account):
            return "operating"
        if any(keyword in haystack for keyword in INVESTING_ASSET_KEYWORDS):
            return "investing"
        if any(keyword in haystack for keyword in CURRENT_ASSET_KEYWORDS):
            return "operating"
        return "investing"

    return "operating"


def _cash_equivalent_accounts(
    *,
    organization=None,
    branch=None,
    fiscal_year=None,
) -> List[ChartOfAccount]:
    queryset = scope_account_queryset(
        ChartOfAccount.objects.filter(
            is_ledger=True,
            is_active=True,
            account_type="asset",
        ).select_related("parent"),
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    ).order_by("code", "sort_order", "id")

    return [account for account in queryset if is_cash_equivalent_account(account)]


def _posting_scope(
    *,
    organization=None,
    branch=None,
    fiscal_year=None,
):
    queryset = LedgerPosting.objects.select_related("account", "journal_entry")
    if organization:
        queryset = queryset.filter(journal_entry__organization=organization)
    if branch:
        queryset = queryset.filter(journal_entry__branch=branch)
    if fiscal_year:
        queryset = queryset.filter(journal_entry__fiscal_year=fiscal_year)
    return queryset


def _build_section_rows(
    section_account_map: Dict[str, Dict[int, Dict[str, Any]]],
    *,
    show_zero_balances: bool,
) -> Dict[str, Dict[str, Any]]:
    sections: Dict[str, Dict[str, Any]] = {}

    for key, meta in SECTION_META.items():
        rows = sorted(
            section_account_map[key].values(),
            key=lambda row: (row.get("code", ""), row.get("name", ""), row.get("id", 0)),
        )
        if not show_zero_balances:
            rows = [row for row in rows if row["amount"] != ZERO]

        total = quantize_amount(sum((row["amount"] for row in rows), ZERO))
        sections[key] = {
            "key": key,
            "label": meta["label"],
            "rows": rows,
            "total": total,
        }

    return sections


def _build_cash_account_rows(
    cash_accounts: Iterable[ChartOfAccount],
    *,
    date_from,
    date_to,
    organization=None,
    branch=None,
    fiscal_year=None,
    show_zero_balances: bool,
) -> Dict[str, Any]:
    accounts = list(cash_accounts)
    if not accounts:
        return {
            "rows": [],
            "opening_total": ZERO,
            "inflow_total": ZERO,
            "outflow_total": ZERO,
            "net_change_total": ZERO,
            "closing_total": ZERO,
        }

    account_ids = [account.pk for account in accounts]
    scoped_postings = _posting_scope(
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    ).filter(account_id__in=account_ids)

    opening_map = {
        item["account_id"]: signed_balance("asset", item["debit_total"], item["credit_total"])
        for item in scoped_postings.filter(posting_date__lt=date_from)
        .values("account_id")
        .annotate(
            debit_total=Coalesce(Sum("debit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
            credit_total=Coalesce(Sum("credit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
        )
    }
    period_map = {
        item["account_id"]: {
            "debit_total": quantize_amount(item["debit_total"]),
            "credit_total": quantize_amount(item["credit_total"]),
        }
        for item in scoped_postings.filter(posting_date__gte=date_from, posting_date__lte=date_to)
        .values("account_id")
        .annotate(
            debit_total=Coalesce(Sum("debit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
            credit_total=Coalesce(Sum("credit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
        )
    }

    rows = []
    opening_total = ZERO
    inflow_total = ZERO
    outflow_total = ZERO
    closing_total = ZERO

    for account in accounts:
        period_totals = period_map.get(account.pk, {})
        opening_balance = quantize_amount(opening_map.get(account.pk))
        inflow = quantize_amount(period_totals.get("debit_total"))
        outflow = quantize_amount(period_totals.get("credit_total"))
        net_change = quantize_amount(inflow - outflow)
        closing_balance = quantize_amount(opening_balance + net_change)

        if not show_zero_balances and not any([opening_balance, inflow, outflow, closing_balance]):
            continue

        rows.append(
            {
                "id": account.pk,
                "code": account.code or "",
                "name": account.name,
                "full_path": account.full_path,
                "opening_balance": opening_balance,
                "inflow": inflow,
                "outflow": outflow,
                "net_change": net_change,
                "closing_balance": closing_balance,
                "is_negative_closing": closing_balance < ZERO,
            }
        )
        opening_total += opening_balance
        inflow_total += inflow
        outflow_total += outflow
        closing_total += closing_balance

    opening_total = quantize_amount(opening_total)
    inflow_total = quantize_amount(inflow_total)
    outflow_total = quantize_amount(outflow_total)
    closing_total = quantize_amount(closing_total)

    return {
        "rows": rows,
        "opening_total": opening_total,
        "inflow_total": inflow_total,
        "outflow_total": outflow_total,
        "net_change_total": quantize_amount(inflow_total - outflow_total),
        "closing_total": closing_total,
    }


def build_cash_flow_report(
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

    cash_accounts = _cash_equivalent_accounts(
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    )
    cash_account_ids = {account.pk for account in cash_accounts}

    period_postings = _posting_scope(
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    ).filter(posting_date__gte=start_date, posting_date__lte=end_date).order_by(
        "journal_entry_id",
        "line_order",
        "id",
    )

    entry_map: Dict[int, List[LedgerPosting]] = defaultdict(list)
    for posting in period_postings:
        entry_map[posting.journal_entry_id].append(posting)

    section_account_map: Dict[str, Dict[int, Dict[str, Any]]] = {
        "operating": {},
        "investing": {},
        "financing": {},
    }

    # Direct-method statement: every non-cash counterpart line explains the cash
    # movement created by the journal entry's cash/bank posting.
    for postings in entry_map.values():
        has_cash_account = any(posting.account_id in cash_account_ids for posting in postings)
        if not has_cash_account:
            continue

        non_cash_postings = [posting for posting in postings if posting.account_id not in cash_account_ids]
        if not non_cash_postings:
            continue

        for posting in non_cash_postings:
            amount = quantize_amount(posting.credit_amount - posting.debit_amount)
            section_key = _classify_counterparty_account(posting.account)
            bucket = section_account_map[section_key].setdefault(
                posting.account_id,
                {
                    "id": posting.account_id,
                    "code": posting.account.code or "",
                    "name": posting.account.name,
                    "full_path": posting.account.full_path,
                    "amount": ZERO,
                    "entry_count": 0,
                },
            )
            bucket["amount"] = quantize_amount(bucket["amount"] + amount)
            bucket["entry_count"] += 1

    sections = _build_section_rows(
        section_account_map,
        show_zero_balances=show_zero_balances,
    )
    cash_breakdown = _build_cash_account_rows(
        cash_accounts,
        date_from=start_date,
        date_to=end_date,
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
        show_zero_balances=show_zero_balances,
    )

    operating_total = sections["operating"]["total"]
    investing_total = sections["investing"]["total"]
    financing_total = sections["financing"]["total"]
    net_change_in_cash = cash_breakdown["net_change_total"]
    classified_net_change = quantize_amount(operating_total + investing_total + financing_total)
    reconciliation_gap = quantize_amount(net_change_in_cash - classified_net_change)

    export_rows: List[Dict[str, Any]] = []
    for section in sections.values():
        for row in section["rows"]:
            export_rows.append(
                {
                    "section": section["label"],
                    "code": row["code"],
                    "account": row["full_path"],
                    "flow_type": "Inflow" if row["amount"] > ZERO else ("Outflow" if row["amount"] < ZERO else "Neutral"),
                    "amount": row["amount"],
                }
            )

    for row in cash_breakdown["rows"]:
        export_rows.extend(
            [
                {
                    "section": "Cash & Cash Equivalents",
                    "code": row["code"],
                    "account": f"{row['full_path']} | Opening Balance",
                    "flow_type": "Opening",
                    "amount": row["opening_balance"],
                },
                {
                    "section": "Cash & Cash Equivalents",
                    "code": row["code"],
                    "account": f"{row['full_path']} | Net Change",
                    "flow_type": "Movement",
                    "amount": row["net_change"],
                },
                {
                    "section": "Cash & Cash Equivalents",
                    "code": row["code"],
                    "account": f"{row['full_path']} | Closing Balance",
                    "flow_type": "Closing",
                    "amount": row["closing_balance"],
                },
            ]
        )

    export_rows.extend(
        [
            {
                "section": "Summary",
                "code": "",
                "account": "Net Cash From Operating Activities",
                "flow_type": "Summary",
                "amount": operating_total,
            },
            {
                "section": "Summary",
                "code": "",
                "account": "Net Cash From Investing Activities",
                "flow_type": "Summary",
                "amount": investing_total,
            },
            {
                "section": "Summary",
                "code": "",
                "account": "Net Cash From Financing Activities",
                "flow_type": "Summary",
                "amount": financing_total,
            },
            {
                "section": "Summary",
                "code": "",
                "account": "Net Increase / (Decrease) in Cash",
                "flow_type": "Summary",
                "amount": net_change_in_cash,
            },
            {
                "section": "Summary",
                "code": "",
                "account": "Opening Cash & Cash Equivalents",
                "flow_type": "Summary",
                "amount": cash_breakdown["opening_total"],
            },
            {
                "section": "Summary",
                "code": "",
                "account": "Closing Cash & Cash Equivalents",
                "flow_type": "Summary",
                "amount": cash_breakdown["closing_total"],
            },
        ]
    )

    return {
        "report_title": "Cash Flow Statement",
        "generated_at": timezone.localtime(),
        "organization": organization,
        "branch": branch,
        "fiscal_year": fiscal_year,
        "date_from": start_date,
        "date_to": end_date,
        "show_zero_balances": show_zero_balances,
        "method": "Direct Method",
        "operating_section": sections["operating"],
        "investing_section": sections["investing"],
        "financing_section": sections["financing"],
        "cash_accounts": cash_breakdown["rows"],
        "rows": export_rows,
        "summary": {
            "cash_accounts_detected": len(cash_accounts),
            "opening_cash": cash_breakdown["opening_total"],
            "cash_inflow": cash_breakdown["inflow_total"],
            "cash_outflow": cash_breakdown["outflow_total"],
            "net_cash_from_operating": operating_total,
            "net_cash_from_investing": investing_total,
            "net_cash_from_financing": financing_total,
            "classified_net_change": classified_net_change,
            "net_change_in_cash": net_change_in_cash,
            "closing_cash": cash_breakdown["closing_total"],
            "reconciliation_gap": reconciliation_gap,
        },
    }
