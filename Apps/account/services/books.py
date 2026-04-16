from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List

from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from ..models import ChartOfAccount, JournalEntry, JournalEntryStatus, LedgerPosting, VoucherType
from .reporting import NORMAL_BALANCE_BY_TYPE, ZERO, quantize_amount, scope_account_queryset, signed_balance


DECIMAL_OUTPUT = DecimalField(max_digits=18, decimal_places=2)
SPECIAL_BOOK_KEYWORDS = {
    "cash": ("cash", "petty cash", "cash in hand", "cash a/c"),
    "bank": ("bank", "current account", "saving account", "savings account", "cheque", "deposit account"),
}


def format_balance_display(account_type: str, amount) -> str:
    normalized = quantize_amount(amount)
    normal_side = NORMAL_BALANCE_BY_TYPE.get(account_type, "debit")
    if normalized >= ZERO:
        label = "Dr" if normal_side == "debit" else "Cr"
    else:
        label = "Cr" if normal_side == "debit" else "Dr"
    return f"{abs(normalized):,.2f} {label}"


def _posting_scope(*, organization=None, branch=None, fiscal_year=None):
    queryset = LedgerPosting.objects.select_related("account", "voucher_type", "journal_entry")
    if organization:
        queryset = queryset.filter(journal_entry__organization=organization)
    if branch:
        queryset = queryset.filter(journal_entry__branch=branch)
    if fiscal_year:
        queryset = queryset.filter(journal_entry__fiscal_year=fiscal_year)
    return queryset


def _account_label(account: ChartOfAccount) -> str:
    return f"{account.code or 'AUTO'} - {account.full_path}"


def _distinct_labels(items: Iterable[str]) -> str:
    labels = []
    seen = set()
    for item in items:
        value = (item or "").strip()
        if not value or value in seen:
            continue
        labels.append(value)
        seen.add(value)
    return ", ".join(labels)


def _counterpart_map(postings: List[LedgerPosting]) -> Dict[int, str]:
    entry_ids = {posting.journal_entry_id for posting in postings}
    if not entry_ids:
        return {}

    entry_postings = (
        LedgerPosting.objects.filter(journal_entry_id__in=entry_ids)
        .select_related("account")
        .order_by("journal_entry_id", "line_order", "id")
    )
    grouped: Dict[int, List[LedgerPosting]] = defaultdict(list)
    for item in entry_postings:
        grouped[item.journal_entry_id].append(item)

    counterpart_map = {}
    for posting in postings:
        labels = [
            _account_label(item.account)
            for item in grouped.get(posting.journal_entry_id, [])
            if item.account_id != posting.account_id
        ]
        counterpart_map[posting.pk] = _distinct_labels(labels)
    return counterpart_map


def is_special_book_account(account: ChartOfAccount, book_type: str) -> bool:
    if not account or not account.is_ledger or account.account_type != "asset":
        return False
    keywords = SPECIAL_BOOK_KEYWORDS.get(book_type, ())
    haystack = " ".join(
        [
            str(account.code or ""),
            str(account.name or ""),
            str(account.full_path or ""),
        ]
    ).lower()
    return any(keyword in haystack for keyword in keywords)


def get_special_book_accounts(
    *,
    book_type: str,
    organization=None,
    branch=None,
    fiscal_year=None,
) -> List[ChartOfAccount]:
    queryset = scope_account_queryset(
        ChartOfAccount.objects.filter(is_ledger=True, is_active=True).select_related("parent"),
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    ).order_by("code", "sort_order", "id")
    return [account for account in queryset if is_special_book_account(account, book_type)]


def build_account_statement_section(
    account: ChartOfAccount,
    *,
    date_from,
    date_to,
    organization=None,
    branch=None,
    fiscal_year=None,
) -> Dict[str, Any]:
    scoped_postings = _posting_scope(
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    ).filter(account=account)

    opening_totals = scoped_postings.filter(posting_date__lt=date_from).aggregate(
        debit_total=Coalesce(Sum("debit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
        credit_total=Coalesce(Sum("credit_amount"), Value(ZERO, output_field=DECIMAL_OUTPUT)),
    )
    opening_balance = signed_balance(
        account.account_type,
        opening_totals["debit_total"],
        opening_totals["credit_total"],
    )

    period_postings = list(
        scoped_postings.filter(posting_date__gte=date_from, posting_date__lte=date_to).order_by(
            "posting_date",
            "entry_no",
            "line_order",
            "id",
        )
    )
    counterparts = _counterpart_map(period_postings)

    running_balance = opening_balance
    total_debit = ZERO
    total_credit = ZERO
    rows = []

    for posting in period_postings:
        debit_amount = quantize_amount(posting.debit_amount)
        credit_amount = quantize_amount(posting.credit_amount)
        total_debit += debit_amount
        total_credit += credit_amount
        running_balance += signed_balance(account.account_type, debit_amount, credit_amount)
        rows.append(
            {
                "posting_date": posting.posting_date,
                "entry_no": posting.entry_no,
                "voucher_type": posting.voucher_type.name if posting.voucher_type_id else "",
                "reference_no": posting.reference_no,
                "narration": posting.narration,
                "description": posting.description,
                "counterpart": counterparts.get(posting.pk, ""),
                "debit_amount": debit_amount,
                "credit_amount": credit_amount,
                "running_balance": quantize_amount(running_balance),
                "running_balance_display": format_balance_display(account.account_type, running_balance),
                "partner_type": posting.partner_type,
                "partner_id": posting.partner_id,
                "cost_center": posting.cost_center,
                "is_reversal": posting.is_reversal,
            }
        )

    closing_balance = quantize_amount(running_balance)
    transaction_count = len(rows)

    return {
        "account": account,
        "account_label": _account_label(account),
        "opening_balance": quantize_amount(opening_balance),
        "opening_balance_display": format_balance_display(account.account_type, opening_balance),
        "rows": rows,
        "total_debit": quantize_amount(total_debit),
        "total_credit": quantize_amount(total_credit),
        "closing_balance": closing_balance,
        "closing_balance_display": format_balance_display(account.account_type, closing_balance),
        "transaction_count": transaction_count,
    }


def build_general_ledger_report(
    *,
    account: ChartOfAccount,
    date_from,
    date_to,
    organization=None,
    branch=None,
    fiscal_year=None,
) -> Dict[str, Any]:
    section = build_account_statement_section(
        account,
        date_from=date_from,
        date_to=date_to,
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    )

    export_rows = [
        {
            "account": section["account_label"],
            "date": date_from,
            "entry_no": "",
            "voucher_type": "",
            "reference_no": "",
            "description": "Opening Balance",
            "counterpart": "",
            "debit": ZERO,
            "credit": ZERO,
            "running_balance": section["opening_balance_display"],
        }
    ]
    for row in section["rows"]:
        export_rows.append(
            {
                "account": section["account_label"],
                "date": row["posting_date"],
                "entry_no": row["entry_no"],
                "voucher_type": row["voucher_type"],
                "reference_no": row["reference_no"],
                "description": row["description"] or row["narration"],
                "counterpart": row["counterpart"],
                "debit": row["debit_amount"],
                "credit": row["credit_amount"],
                "running_balance": row["running_balance_display"],
            }
        )
    export_rows.append(
        {
            "account": section["account_label"],
            "date": date_to,
            "entry_no": "",
            "voucher_type": "",
            "reference_no": "",
            "description": "Closing Balance",
            "counterpart": "",
            "debit": section["total_debit"],
            "credit": section["total_credit"],
            "running_balance": section["closing_balance_display"],
        }
    )

    return {
        "report_title": "General Ledger",
        "generated_at": timezone.localtime(),
        "organization": organization,
        "branch": branch,
        "fiscal_year": fiscal_year,
        "date_from": date_from,
        "date_to": date_to,
        "account_sections": [section],
        "rows": export_rows,
        "summary": {
            "accounts": 1,
            "transactions": section["transaction_count"],
            "opening_balance": section["opening_balance"],
            "total_debit": section["total_debit"],
            "total_credit": section["total_credit"],
            "closing_balance": section["closing_balance"],
        },
    }


def build_special_book_report(
    *,
    book_type: str,
    date_from,
    date_to,
    organization=None,
    branch=None,
    fiscal_year=None,
    account: ChartOfAccount | None = None,
) -> Dict[str, Any]:
    accounts = [account] if account else get_special_book_accounts(
        book_type=book_type,
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
    )

    sections = []
    export_rows = []
    total_opening = ZERO
    total_debit = ZERO
    total_credit = ZERO
    total_closing = ZERO
    total_transactions = 0

    for ledger_account in accounts:
        section = build_account_statement_section(
            ledger_account,
            date_from=date_from,
            date_to=date_to,
            organization=organization,
            branch=branch,
            fiscal_year=fiscal_year,
        )
        if not section["rows"] and section["opening_balance"] == ZERO and section["closing_balance"] == ZERO:
            continue
        sections.append(section)
        total_opening += section["opening_balance"]
        total_debit += section["total_debit"]
        total_credit += section["total_credit"]
        total_closing += section["closing_balance"]
        total_transactions += section["transaction_count"]

        export_rows.append(
            {
                "account": section["account_label"],
                "date": date_from,
                "entry_no": "",
                "voucher_type": "",
                "reference_no": "",
                "description": "Opening Balance",
                "counterpart": "",
                "debit": ZERO,
                "credit": ZERO,
                "running_balance": section["opening_balance_display"],
            }
        )
        for row in section["rows"]:
            export_rows.append(
                {
                    "account": section["account_label"],
                    "date": row["posting_date"],
                    "entry_no": row["entry_no"],
                    "voucher_type": row["voucher_type"],
                    "reference_no": row["reference_no"],
                    "description": row["description"] or row["narration"],
                    "counterpart": row["counterpart"],
                    "debit": row["debit_amount"],
                    "credit": row["credit_amount"],
                    "running_balance": row["running_balance_display"],
                }
            )
        export_rows.append(
            {
                "account": section["account_label"],
                "date": date_to,
                "entry_no": "",
                "voucher_type": "",
                "reference_no": "",
                "description": "Closing Balance",
                "counterpart": "",
                "debit": section["total_debit"],
                "credit": section["total_credit"],
                "running_balance": section["closing_balance_display"],
            }
        )

    label = "Cash Book" if book_type == "cash" else "Bank Book"
    return {
        "report_title": label,
        "generated_at": timezone.localtime(),
        "organization": organization,
        "branch": branch,
        "fiscal_year": fiscal_year,
        "date_from": date_from,
        "date_to": date_to,
        "account_sections": sections,
        "book_type": book_type,
        "rows": export_rows,
        "summary": {
            "accounts": len(sections),
            "transactions": total_transactions,
            "opening_balance": quantize_amount(total_opening),
            "total_debit": quantize_amount(total_debit),
            "total_credit": quantize_amount(total_credit),
            "closing_balance": quantize_amount(total_closing),
        },
    }


def build_day_book_report(
    *,
    date_from,
    date_to,
    organization=None,
    branch=None,
    fiscal_year=None,
    voucher_type: VoucherType | None = None,
) -> Dict[str, Any]:
    queryset = (
        JournalEntry.objects.filter(status=JournalEntryStatus.POSTED, date__gte=date_from, date__lte=date_to)
        .select_related("voucher_type", "organization", "branch", "fiscal_year")
        .prefetch_related("lines__account")
        .order_by("date", "id")
    )
    if organization:
        queryset = queryset.filter(organization=organization)
    if branch:
        queryset = queryset.filter(branch=branch)
    if fiscal_year:
        queryset = queryset.filter(fiscal_year=fiscal_year)
    if voucher_type:
        queryset = queryset.filter(voucher_type=voucher_type)

    entries = []
    export_rows = []
    total_debit = ZERO
    total_credit = ZERO

    for entry in queryset:
        line_rows = []
        for line in entry.lines.all():
            line_rows.append(
                {
                    "account": _account_label(line.account) if line.account_id else "",
                    "description": line.description,
                    "entry_side": "Dr" if line.entry_side == "debit" else "Cr",
                    "amount": quantize_amount(line.amount),
                    "cost_center": line.cost_center,
                }
            )
        total_debit += quantize_amount(entry.total_debit)
        total_credit += quantize_amount(entry.total_credit)
        entries.append(
            {
                "date": entry.date,
                "entry_no": entry.entry_no,
                "voucher_type": entry.voucher_type.name if entry.voucher_type_id else "",
                "reference_no": entry.reference_no,
                "narration": entry.narration,
                "total_debit": quantize_amount(entry.total_debit),
                "total_credit": quantize_amount(entry.total_credit),
                "lines": line_rows,
                "line_count": len(line_rows),
            }
        )
        export_rows.append(
            {
                "date": entry.date,
                "entry_no": entry.entry_no,
                "voucher_type": entry.voucher_type.name if entry.voucher_type_id else "",
                "reference_no": entry.reference_no,
                "narration": entry.narration,
                "line_summary": " | ".join(
                    f"{line['account']} {line['entry_side']} {line['amount']:,.2f}" for line in line_rows
                ),
                "total_debit": quantize_amount(entry.total_debit),
                "total_credit": quantize_amount(entry.total_credit),
            }
        )

    return {
        "report_title": "Day Book",
        "generated_at": timezone.localtime(),
        "organization": organization,
        "branch": branch,
        "fiscal_year": fiscal_year,
        "date_from": date_from,
        "date_to": date_to,
        "voucher_type": voucher_type,
        "entries": entries,
        "rows": export_rows,
        "summary": {
            "entries": len(entries),
            "lines": sum(item["line_count"] for item in entries),
            "total_debit": quantize_amount(total_debit),
            "total_credit": quantize_amount(total_credit),
        },
    }
