from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from nepanest.common.helpers.helper import ad_to_bs
from nepanest.modules.leave.models import Holiday


class HolidayCalendarDatesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        holidays = (
            Holiday.objects.filter(holiday_calendar__is_active=True)
            .select_related("holiday_calendar")
            .order_by("date", "name", "id")
        )

        holiday_map = {}
        for holiday in holidays:
            bs_date = ad_to_bs(holiday.date)
            bs_key = f"{bs_date.year:04d}-{bs_date.month:02d}-{bs_date.day:02d}"
            holiday_map.setdefault(bs_key, []).append(
                {
                    "name": holiday.name,
                    "calendar": holiday.holiday_calendar.name,
                    "is_optional": holiday.is_optional,
                    "is_half_day": holiday.is_half_day,
                }
            )

        return JsonResponse(
            {
                "dates": holiday_map,
                "count": len(holiday_map),
            }
        )
