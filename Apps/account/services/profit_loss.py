from __future__ import annotations

from typing import Any, Dict, List

from django.utils import timezone

from .reporting import (
    ZERO,
    build_account_balance_snapshot,
    build_section_rows,
    flatten_export_rows,
    quantize_amount,
)


SECTION_META = {
    "income": {"label": "Income"},
    "expense": {"label": "Expenses"},
}


def calculate_profit_loss_summary(
    *,
    organization=None,
    branch=None,
    fiscal_year=None,
    date_from=None,
    date_to=None,
) -> Dict[str, Any]:
    snapshot = build_account_balance_snapshot(
        report_type="profit_loss",
        account_types=["income", "expense"],
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
        date_from=date_from,
        date_to=date_to,
    )

    total_income = quantize_amount(snapshot["totals_by_type"].get("income", ZERO))
    total_expenses = quantize_amount(snapshot["totals_by_type"].get("expense", ZERO))
    net_result = quantize_amount(total_income - total_expenses)

    snapshot.update(
        {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_result": net_result,
            "is_profit": net_result >= ZERO,
            "net_result_label": "Net Profit" if net_result >= ZERO else "Net Loss",
        }
    )
    return snapshot


def build_profit_loss_report(
    *,
    organization=None,
    branch=None,
    fiscal_year=None,
    date_from=None,
    date_to=None,
    show_zero_balances: bool = False,
) -> Dict[str, Any]:
    today = timezone.localdate()
    start_date = date_from or (fiscal_year.start_date if fiscal_year else None)
    end_date = date_to or today

    if fiscal_year:
        if start_date and start_date < fiscal_year.start_date:
            start_date = fiscal_year.start_date
        if end_date > fiscal_year.end_date:
            end_date = fiscal_year.end_date

    summary = calculate_profit_loss_summary(
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
        date_from=start_date,
        date_to=end_date,
    )

    children_map = summary["children_map"]
    rolled_balance_map = summary["rolled_balance_map"]

    sections: Dict[str, Dict[str, Any]] = {}
    export_rows: List[Dict[str, Any]] = []

    for account_type, meta in SECTION_META.items():
        root_accounts = [
            account
            for account in children_map.get(None, [])
            if account.account_type == account_type
        ]
        rows = build_section_rows(
            root_accounts,
            balance_map=rolled_balance_map,
            children_map=children_map,
            show_zero_balances=show_zero_balances,
        )
        total = quantize_amount(sum((rolled_balance_map.get(account.pk, ZERO) for account in root_accounts), ZERO))
        sections[account_type] = {
            "key": account_type,
            "label": meta["label"],
            "rows": rows,
            "total": total,
        }
        export_rows.extend(flatten_export_rows(meta["label"], rows))

    export_rows.extend(
        [
            {
                "section": "Summary",
                "code": "",
                "account": "Total Income",
                "level": 0,
                "account_kind": "Summary",
                "amount": summary["total_income"],
            },
            {
                "section": "Summary",
                "code": "",
                "account": "Total Expenses",
                "level": 0,
                "account_kind": "Summary",
                "amount": summary["total_expenses"],
            },
            {
                "section": "Summary",
                "code": "",
                "account": summary["net_result_label"],
                "level": 0,
                "account_kind": "Summary",
                "amount": summary["net_result"],
            },
        ]
    )

    return {
        "report_title": "Profit & Loss Statement",
        "generated_at": timezone.localtime(),
        "organization": organization,
        "branch": branch,
        "fiscal_year": fiscal_year,
        "date_from": start_date,
        "date_to": end_date,
        "show_zero_balances": show_zero_balances,
        "income_section": sections["income"],
        "expense_section": sections["expense"],
        "rows": export_rows,
        "summary": {
            "total_income": summary["total_income"],
            "total_expenses": summary["total_expenses"],
            "net_result": summary["net_result"],
            "net_result_label": summary["net_result_label"],
            "is_profit": summary["is_profit"],
        },
    }
