from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from django.utils import timezone

from nepanest.modules.leave.models import LeaveBalance


def build_leave_balance_summary_report(*, employee=None, leave_type=None, year=None) -> Dict[str, Any]:
    queryset = LeaveBalance.objects.select_related(
        "employee",
        "employee__user",
        "leave_type",
    ).all()

    if employee:
        queryset = queryset.filter(employee=employee)
    if leave_type:
        queryset = queryset.filter(leave_type=leave_type)
    if year:
        queryset = queryset.filter(year=year)

    total_opening = Decimal("0")
    total_accrued = Decimal("0")
    total_used = Decimal("0")
    total_encashed = Decimal("0")
    total_balance = Decimal("0")
    rows = []

    for item in queryset.order_by("-year", "employee__employee_id", "leave_type__name"):
        total_opening += item.opening_balance or Decimal("0")
        total_accrued += item.accrued or Decimal("0")
        total_used += item.used or Decimal("0")
        total_encashed += item.encashed or Decimal("0")
        total_balance += item.balance or Decimal("0")
        rows.append(
            {
                "employee_id": item.employee.employee_id,
                "employee_name": item.employee.full_name or item.employee.user.username,
                "leave_type": item.leave_type.name,
                "year": item.year,
                "opening_balance": item.opening_balance,
                "accrued": item.accrued,
                "used": item.used,
                "encashed": item.encashed,
                "balance": item.balance,
                "updated_at": timezone.localtime(item.updated_at).strftime("%Y-%m-%d %H:%M"),
            }
        )

    return {
        "report_title": "Leave Balance Summary Report",
        "generated_at": timezone.localtime(),
        "selected_employee": employee,
        "selected_leave_type": leave_type,
        "selected_year": year,
        "rows": rows,
        "summary": {
            "records": len(rows),
            "total_opening": total_opening,
            "total_accrued": total_accrued,
            "total_used": total_used,
            "total_encashed": total_encashed,
            "total_balance": total_balance,
        },
    }
