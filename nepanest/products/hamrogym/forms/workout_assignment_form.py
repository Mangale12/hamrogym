from django import forms

from .workout_plan_form import _apply_bootstrap_widgets
from ..models import WorkoutAssignment


class WorkoutAssignmentForm(forms.ModelForm):
    class Meta:
        model = WorkoutAssignment
        fields = [
            "member",
            "trainer",
            "workout_plan",
            "start_date",
            "end_date",
            "status",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trainer"].required = False
        self.fields["end_date"].required = False
        _apply_bootstrap_widgets(self)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "End date cannot be earlier than start date.")
        return cleaned_data
