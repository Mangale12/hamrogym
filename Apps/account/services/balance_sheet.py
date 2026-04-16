from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from django.utils import timezone

from .profit_loss import calculate_profit_loss_summary
from .reporting import (
    ZERO,
    build_account_balance_snapshot,
    build_section_rows,
    flatten_export_rows,
    quantize_amount,
)


SECTION_META = {
    "asset": {"label": "Assets", "side": "left"},
    "liability": {"label": "Liabilities", "side": "right"},
    "equity": {"label": "Equity", "side": "right"},
}


def build_balance_sheet_report(
    *,
    organization=None,
    branch=None,
    fiscal_year=None,
    as_of_date=None,
    show_zero_balances: bool = False,
) -> Dict[str, Any]:
    today = timezone.localdate()
    cutoff_date = as_of_date or today
    if fiscal_year and cutoff_date > fiscal_year.end_date:
        cutoff_date = fiscal_year.end_date

    snapshot = build_account_balance_snapshot(
        report_type="balance_sheet",
        account_types=["asset", "liability", "equity"],
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
        date_to=cutoff_date,
    )

    profit_loss_summary = calculate_profit_loss_summary(
        organization=organization,
        branch=branch,
        fiscal_year=fiscal_year,
        date_from=fiscal_year.start_date if fiscal_year else None,
        date_to=cutoff_date,
    )
    current_earnings = quantize_amount(profit_loss_summary["net_result"])

    children_map = snapshot["children_map"]
    rolled_balance_map = snapshot["rolled_balance_map"]

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
            "side": meta["side"],
            "rows": rows,
            "total": total,
        }
        export_rows.extend(flatten_export_rows(meta["label"], rows))

    current_earnings_row = {
        "id": "current-period-earnings",
        "code": "PL-CURRENT",
        "name": "Current Period Earnings",
        "account_type": "equity",
        "level": 1,
        "depth": 0,
        "indent_px": 0,
        "is_group": False,
        "is_ledger": False,
        "is_derived": True,
        "amount": current_earnings,
        "is_negative": current_earnings < Decimal("0.00"),
    }
    sections["equity"]["derived_rows"] = [current_earnings_row] if show_zero_balances or current_earnings != ZERO else []
    sections["equity"]["total_before_derived"] = sections["equity"]["total"]
    sections["equity"]["total"] = quantize_amount(sections["equity"]["total"] + current_earnings)

    if sections["equity"]["derived_rows"]:
        export_rows.append(
            {
                "section": "Equity",
                "code": current_earnings_row["code"],
                "account": current_earnings_row["name"],
                "level": current_earnings_row["level"],
                "account_kind": "Derived",
                "amount": current_earnings_row["amount"],
            }
        )

    total_assets = sections["asset"]["total"]
    total_liabilities = sections["liability"]["total"]
    total_equity = sections["equity"]["total"]
    total_liabilities_and_equity = quantize_amount(total_liabilities + total_equity)
    difference = quantize_amount(total_assets - total_liabilities_and_equity)

    export_rows.extend(
        [
            {
                "section": "Summary",
                "code": "",
                "account": "Total Assets",
                "level": 0,
                "account_kind": "Summary",
                "amount": total_assets,
            },
            {
                "section": "Summary",
                "code": "",
                "account": "Total Liabilities",
                "level": 0,
                "account_kind": "Summary",
                "amount": total_liabilities,
            },
            {
                "section": "Summary",
                "code": "",
                "account": "Total Equity",
                "level": 0,
                "account_kind": "Summary",
                "amount": total_equity,
            },
            {
                "section": "Summary",
                "code": "",
                "account": "Difference",
                "level": 0,
                "account_kind": "Summary",
                "amount": difference,
            },
        ]
    )

    return {
        "report_title": "Balance Sheet",
        "generated_at": timezone.localtime(),
        "organization": organization,
        "branch": branch,
        "fiscal_year": fiscal_year,
        "as_of_date": cutoff_date,
        "show_zero_balances": show_zero_balances,
        "asset_section": sections["asset"],
        "liability_section": sections["liability"],
        "equity_section": sections["equity"],
        "rows": export_rows,
        "summary": {
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "current_earnings": current_earnings,
            "current_earnings_label": profit_loss_summary["net_result_label"],
            "total_liabilities_and_equity": total_liabilities_and_equity,
            "difference": difference,
        },
    }
