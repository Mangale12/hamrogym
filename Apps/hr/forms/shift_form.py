from django import forms

from ..models import Shift


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = [
            "name",
            "code",
            "start_time",
            "end_time",
            "break_start_time",
            "break_end_time",
            "grace_start_time",
            "grace_end_time",
            "is_active",
            "break_duration",
        ]
