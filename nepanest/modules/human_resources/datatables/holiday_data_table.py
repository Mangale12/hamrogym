from core.datatables.views import BaseDataTableView

from nepanest.modules.leave.models import HolidayCalendar


HOLIDAY_CALENDAR_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("year", "year"),
    ("description", "description"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class HolidayCalendarDataTableView(BaseDataTableView):
    model = HolidayCalendar
    columns = HOLIDAY_CALENDAR_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "description",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "code",
        "year",
        "is_active",
    ]
