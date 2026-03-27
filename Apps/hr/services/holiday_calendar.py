from datetime import timedelta

from Apps.hr.models import HolidayCalendar


def get_active_holiday_calendar(*, year: int):
    return (
        HolidayCalendar.objects.filter(year=year, is_active=True)
        .order_by("name", "id")
        .first()
    )


def get_holiday_dates(*, year: int):
    calendar = get_active_holiday_calendar(year=year)
    if calendar is None:
        return set()
    return set(calendar.holidays.values_list("date", flat=True))


def get_weekly_off_weekdays(*, year: int):
    calendar = get_active_holiday_calendar(year=year)
    if calendar is None:
        return set()
    return set(
        calendar.weekly_off_rules.filter(is_active=True).values_list("weekday", flat=True)
    )


def iter_dates(start_date, end_date):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)
