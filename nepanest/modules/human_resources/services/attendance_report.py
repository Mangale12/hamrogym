from __future__ import annotations

from collections import Counter
from decimal import Decimal
from typing import Any, Dict

from django.utils import timezone

from nepanest.modules.attendance.models import Attendance


def build_employee_attendance_history_report(*, employee=None, date_from, date_to, status: str = "") -> Dict[str, Any]:
    queryset = Attendance.objects.select_related(
        "employee",
        "employee__user",
        "shift",
    ).filter(date__range=(date_from, date_to))

    if employee:
        queryset = queryset.filter(employee=employee)
    if status:
        queryset = queryset.filter(status=status)

    rows = []
    totals = Counter()
    total_work_hours = Decimal("0")

    for attendance in queryset.order_by("employee__employee_id", "-date", "-id"):
        work_hours = attendance.work_hours or Decimal("0")
        total_work_hours += work_hours
        totals["records"] += 1
        totals[attendance.status or "pending"] += 1
        if attendance.is_late:
            totals["late_count"] += 1
        if attendance.is_half_day:
            totals["half_day_count"] += 1

        rows.append(
            {
                "employee_id": attendance.employee.employee_id,
                "employee_name": attendance.employee.full_name or attendance.employee.user.username,
                "date": attendance.date,
                "shift_name": (
                    attendance.shift.name
                    if attendance.shift and getattr(attendance.shift, "name", "")
                    else (attendance.shift.code if attendance.shift and getattr(attendance.shift, "code", "") else "")
                ),
                "check_in_time": attendance.check_in_time.strftime("%H:%M:%S") if attendance.check_in_time else "",
                "check_out_time": attendance.check_out_time.strftime("%H:%M:%S") if attendance.check_out_time else "",
                "work_hours": work_hours,
                "status": attendance.status,
                "is_late": attendance.is_late,
                "is_half_day": attendance.is_half_day,
                "remarks": attendance.remarks,
            }
        )

    return {
        "report_title": "Employee Attendance History Report",
        "generated_at": timezone.localtime(),
        "date_from": date_from,
        "date_to": date_to,
        "selected_employee": employee,
        "selected_status": status,
        "rows": rows,
        "summary": {
            "records": totals["records"],
            "present": totals["present"],
            "late": totals["late"],
            "absent": totals["absent"],
            "half_day_status": totals["half_day"],
            "pending": totals["pending"],
            "late_count": totals["late_count"],
            "half_day_count": totals["half_day_count"],
            "total_work_hours": total_work_hours,
        },
    }
