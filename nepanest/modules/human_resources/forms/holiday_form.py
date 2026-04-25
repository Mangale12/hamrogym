from django import forms

from nepanest.modules.leave.models import HolidayCalendar


class HolidayCalendarForm(forms.ModelForm):
    class Meta:
        model = HolidayCalendar
        fields = [
            "name",
            "code",
            "year",
            "description",
            "is_active",
            "remarks",
        ]
