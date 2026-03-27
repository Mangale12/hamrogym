from decimal import Decimal

from django.core.exceptions import ValidationError

from Apps.hr.models import LeavePolicy
from Apps.hr.services.holiday_calendar import (
    get_holiday_dates,
    get_weekly_off_weekdays,
    iter_dates,
)
from Apps.hr.services.leave_balance import get_available_leave_balance


ZERO = Decimal("0.00")
HALF_DAY = Decimal("0.50")


def get_applicable_leave_policy(*, employee, leave_type, on_date):
    if not employee.employee_type:
        return None

    return (
        LeavePolicy.objects.filter(
            leave_type=leave_type,
            employment_type__code=employee.employee_type,
            is_active=True,
            effective_from__lte=on_date,
            effective_to__isnull=True,
        )
        .order_by("-effective_from", "-id")
        .first()
        or LeavePolicy.objects.filter(
            leave_type=leave_type,
            employment_type__code=employee.employee_type,
            is_active=True,
            effective_from__lte=on_date,
            effective_to__gte=on_date,
        )
        .order_by("-effective_from", "-id")
        .first()
    )


def calculate_leave_days(*, employee, leave_type, start_date, end_date, is_half_day=False):
    if not start_date or not end_date:
        raise ValidationError("Start date and end date are required.")
    if start_date > end_date:
        raise ValidationError({"end_date": "End date must be on or after start date."})
    if is_half_day and start_date != end_date:
        raise ValidationError({"half_day_type": "Half-day leave is only allowed for a single date."})

    holiday_dates = get_holiday_dates(year=start_date.year)
    weekly_offs = get_weekly_off_weekdays(year=start_date.year)
    leave_dates = []
    excluded_dates = []

    for current_date in iter_dates(start_date, end_date):
        if current_date in holiday_dates or current_date.weekday() in weekly_offs:
            excluded_dates.append(current_date)
            continue
        leave_dates.append(current_date)

    total_days = Decimal(len(leave_dates)).quantize(Decimal("0.01"))
    if is_half_day:
        if not leave_dates:
            raise ValidationError({"start_date": "Selected date falls on a holiday or weekly off."})
        total_days = HALF_DAY

    return {
        "total_days": total_days,
        "leave_dates": leave_dates,
        "excluded_dates": excluded_dates,
    }


def validate_leave_request(*, employee, leave_type, start_date, end_date, is_half_day=False, leave_request=None):
    calculation = calculate_leave_days(
        employee=employee,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        is_half_day=is_half_day,
    )
    total_days = calculation["total_days"]
    if total_days <= ZERO:
        raise ValidationError({"start_date": "No working leave days found in the selected range."})

    overlapping_requests = employee.leave_requests.filter(
        start_date__lte=end_date,
        end_date__gte=start_date,
        status__in=["pending", "approved"],
    )
    if leave_request is not None and getattr(leave_request, "pk", None):
        overlapping_requests = overlapping_requests.exclude(pk=leave_request.pk)
    if overlapping_requests.exists():
        raise ValidationError({"start_date": "This employee already has an overlapping leave request."})

    policy = get_applicable_leave_policy(employee=employee, leave_type=leave_type, on_date=start_date)
    if policy is not None:
        if is_half_day and not policy.allow_half_day:
            raise ValidationError({"half_day_type": "This leave type does not allow half-day leave for this employee."})
        if policy.max_consecutive_days and total_days > Decimal(str(policy.max_consecutive_days)):
            raise ValidationError(
                {"end_date": f"Maximum consecutive leave allowed is {policy.max_consecutive_days} days."}
            )
        if total_days > Decimal(str(policy.days_allowed)):
            raise ValidationError(
                {"total_days": f"Policy allows up to {policy.days_allowed} days for this leave type."}
            )
        if not policy.allow_negative_balance:
            available = get_available_leave_balance(employee=employee, leave_type=leave_type, year=start_date.year)
            if total_days > available:
                raise ValidationError({"total_days": f"Available balance is {available}. Requested leave is {total_days}."})

    if leave_type.max_days_per_year and total_days > Decimal(str(leave_type.max_days_per_year)):
        raise ValidationError({"total_days": f"Leave exceeds the per-request limit of {leave_type.max_days_per_year} days."})

    return {
        "policy": policy,
        **calculation,
    }
