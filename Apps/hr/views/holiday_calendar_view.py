import calendar
from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from nepali_datetime import date as bs_date

from core.helpers.helper import ad_to_bs, get_calendar_type
from ..models import HolidayCalendar


class HolidayCalendarView(LoginRequiredMixin, TemplateView):
    template_name = "hr/holiday_calendar_view.html"
    BS_MONTH_NAMES = [
        "Baishakh",
        "Jestha",
        "Ashadh",
        "Shrawan",
        "Bhadra",
        "Ashwin",
        "Kartik",
        "Mangsir",
        "Poush",
        "Magh",
        "Falgun",
        "Chaitra",
    ]
    BS_WEEKDAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    def get_calendar_mode(self):
        return get_calendar_type(self.request)

    def get_selected_year(self):
        raw_year = (self.request.GET.get("year") or "").strip()
        if raw_year.isdigit():
            return int(raw_year)
        if self.calendar_mode == "BS":
            today_bs = ad_to_bs(date.today())
            return today_bs.year
        return date.today().year

    def build_ad_months(self, holiday_map):
        months = []
        for month_number in range(1, 13):
            month_matrix = calendar.Calendar(firstweekday=6).monthdatescalendar(
                self.selected_year,
                month_number,
            )
            weeks = []
            for week in month_matrix:
                week_days = []
                for day in week:
                    is_current_month = day.month == month_number
                    items = holiday_map.get(day, [])
                    week_days.append(
                        {
                            "date": day,
                            "day": day.day,
                            "is_current_month": is_current_month,
                            "is_holiday": bool(items),
                            "holiday_items": items,
                        }
                    )
                weeks.append(week_days)

            months.append(
                {
                    "number": month_number,
                    "name": calendar.month_name[month_number],
                    "weeks": weeks,
                }
            )
        return months

    def build_bs_months(self, holiday_map):
        months = []
        for month_number in range(1, 13):
            first_day = bs_date(self.selected_year, month_number, 1)
            if month_number == 12:
                next_month_first = bs_date(self.selected_year + 1, 1, 1)
            else:
                next_month_first = bs_date(self.selected_year, month_number + 1, 1)
            last_day = next_month_first - timedelta(days=1)

            grid_start = first_day - timedelta(days=first_day.weekday())
            grid_end = last_day + timedelta(days=(6 - last_day.weekday()))

            weeks = []
            cursor = grid_start
            while cursor <= grid_end:
                week_days = []
                for _ in range(7):
                    day_ad = cursor.to_datetime_date()
                    items = holiday_map.get(day_ad, [])
                    week_days.append(
                        {
                            "date": day_ad,
                            "day": cursor.day,
                            "is_current_month": cursor.month == month_number,
                            "is_holiday": bool(items),
                            "holiday_items": items,
                            "display_date": f"{cursor.year:04d}-{cursor.month:02d}-{cursor.day:02d}",
                        }
                    )
                    cursor += timedelta(days=1)
                weeks.append(week_days)

            months.append(
                {
                    "number": month_number,
                    "name": self.BS_MONTH_NAMES[month_number - 1],
                    "weeks": weeks,
                }
            )
        return months

    def get_available_years(self, calendars):
        if self.calendar_mode == "BS":
            years = set()
            for holiday_calendar in calendars:
                for holiday in holiday_calendar.holidays.all():
                    years.add(ad_to_bs(holiday.date).year)
            years_list = sorted(years, reverse=True)
        else:
            years_list = list(
                HolidayCalendar.objects.order_by("-year").values_list("year", flat=True).distinct()
            )

        if self.selected_year not in years_list:
            years_list.insert(0, self.selected_year)
        return years_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.calendar_mode = self.get_calendar_mode()
        self.selected_year = self.get_selected_year()
        calendars = list(
            HolidayCalendar.objects.filter(is_active=True)
            .prefetch_related("holidays")
            .order_by("-year", "name", "id")
        )

        holiday_map = {}
        holiday_rows = []
        for holiday_calendar in calendars:
            for holiday in holiday_calendar.holidays.all():
                if self.calendar_mode == "BS":
                    bs_holiday_date = ad_to_bs(holiday.date)
                    if bs_holiday_date.year != self.selected_year:
                        continue
                    display_date = f"{bs_holiday_date.year:04d}-{bs_holiday_date.month:02d}-{bs_holiday_date.day:02d}"
                else:
                    if holiday_calendar.year != self.selected_year:
                        continue
                    display_date = holiday.date

                holiday_map.setdefault(holiday.date, []).append(
                    {
                        "name": holiday.name,
                        "calendar_name": holiday_calendar.name,
                        "is_optional": holiday.is_optional,
                        "is_half_day": holiday.is_half_day,
                    }
                )
                holiday_rows.append(
                    {
                        "date": holiday.date,
                        "display_date": display_date,
                        "name": holiday.name,
                        "calendar_name": holiday_calendar.name,
                        "is_optional": holiday.is_optional,
                        "is_half_day": holiday.is_half_day,
                    }
                )

        holiday_rows.sort(key=lambda item: (item["date"], item["name"]))
        filtered_calendar_names = {item["calendar_name"] for item in holiday_rows}
        active_calendars = [item for item in calendars if item.name in filtered_calendar_names]

        context.update(
            {
                "page_title": "Holiday Calendar",
                "selected_year": self.selected_year,
                "available_years": self.get_available_years(calendars),
                "active_calendars": active_calendars,
                "months": self.build_bs_months(holiday_map) if self.calendar_mode == "BS" else self.build_ad_months(holiday_map),
                "holiday_rows": holiday_rows,
                "weekday_labels": self.BS_WEEKDAY_LABELS if self.calendar_mode == "BS" else list(calendar.day_abbr),
                "calendar_mode": self.calendar_mode,
            }
        )
        return context
