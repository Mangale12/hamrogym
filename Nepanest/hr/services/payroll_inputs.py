from collections import defaultdict
from decimal import Decimal

from django.db import transaction

from Nepanest.hr.models import (
    Attendance,
    AttendancePayrollSummary,
    LeavePayrollImpact,
    LeaveRequest,
    PayrollAdjustment,
    PayrollRun,
)


ZERO = Decimal("0.00")


def _to_decimal(value) -> Decimal:
    if value in (None, ""):
        return ZERO
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


@transaction.atomic
def build_attendance_payroll_inputs(*, payroll_run: PayrollRun):
    AttendancePayrollSummary.objects.filter(payroll_run=payroll_run).delete()

    summaries = defaultdict(
        lambda: {
            "present_days": ZERO,
            "absent_days": ZERO,
            "half_days": ZERO,
            "leave_days": ZERO,
            "payable_days": ZERO,
            "overtime_hours": ZERO,
            "late_instances": 0,
        }
    )

    attendances = Attendance.objects.filter(
        date__gte=payroll_run.period_start,
        date__lte=payroll_run.period_end,
    ).select_related("employee")

    for attendance in attendances:
        summary = summaries[attendance.employee_id]
        if attendance.status == "present":
            summary["present_days"] += Decimal("1.00")
            summary["payable_days"] += Decimal("1.00")
        elif attendance.status == "late":
            summary["present_days"] += Decimal("1.00")
            summary["payable_days"] += Decimal("1.00")
            summary["late_instances"] += 1
        elif attendance.status == "half_day":
            summary["half_days"] += Decimal("1.00")
            summary["payable_days"] += Decimal("0.50")
        elif attendance.status == "leave":
            summary["leave_days"] += Decimal("1.00")
            summary["payable_days"] += Decimal("1.00")
        elif attendance.status == "absent":
            summary["absent_days"] += Decimal("1.00")

        summary["overtime_hours"] += _to_decimal(attendance.work_hours)

    AttendancePayrollSummary.objects.bulk_create(
        [
            AttendancePayrollSummary(
                payroll_run=payroll_run,
                employee_id=employee_id,
                **values,
            )
            for employee_id, values in summaries.items()
        ]
    )
    return payroll_run.attendance_summaries.count()


@transaction.atomic
def build_leave_payroll_inputs(*, payroll_run: PayrollRun):
    LeavePayrollImpact.objects.filter(payroll_run=payroll_run).delete()

    leave_requests = LeaveRequest.objects.filter(
        status="approved",
        start_date__lte=payroll_run.period_end,
        end_date__gte=payroll_run.period_start,
    ).select_related("employee", "leave_type")

    impacts = []
    for leave_request in leave_requests:
        is_paid = bool(leave_request.leave_type.is_paid)
        deduction_amount = ZERO
        if not is_paid:
            assignment = (
                leave_request.employee.salary_assignments.filter(
                    is_active=True,
                    effective_from__lte=payroll_run.period_end,
                )
                .order_by("-effective_from", "-id")
                .first()
            )
            if assignment and leave_request.total_days:
                daily_rate = _to_decimal(assignment.gross_salary) / Decimal("30.00")
                deduction_amount = (daily_rate * _to_decimal(leave_request.total_days)).quantize(Decimal("0.01"))

        impacts.append(
            LeavePayrollImpact(
                payroll_run=payroll_run,
                employee=leave_request.employee,
                leave_request=leave_request,
                leave_type=leave_request.leave_type,
                days=_to_decimal(leave_request.total_days),
                is_paid=is_paid,
                deduction_amount=deduction_amount,
                remarks=f"Leave impact from request {leave_request.pk}",
            )
        )

    LeavePayrollImpact.objects.bulk_create(impacts)
    return len(impacts)


def get_payroll_adjustments(*, payroll_run: PayrollRun):
    return PayrollAdjustment.objects.filter(payroll_run=payroll_run).select_related(
        "employee",
        "salary_component",
    )
