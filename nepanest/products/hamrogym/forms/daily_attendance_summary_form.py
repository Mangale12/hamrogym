from django import forms

from ..models import DailyAttendanceSummary, Member


class DailyAttendanceSummaryForm(forms.ModelForm):
    class Meta:
        model = DailyAttendanceSummary
        fields = [
            "member",
            "date",
            "total_checkins",
            "total_duration",
            "branch",
            "remarks",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Member.objects.order_by("member_code")
