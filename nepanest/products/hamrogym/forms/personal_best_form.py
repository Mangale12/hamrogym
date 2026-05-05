from django import forms

from .workout_plan_form import _apply_bootstrap_widgets
from ..models import PersonalBest


class PersonalBestForm(forms.ModelForm):
    class Meta:
        model = PersonalBest
        fields = [
            "member",
            "exercise",
            "best_weight",
            "best_reps",
            "best_duration",
            "achieved_on",
        ]
        widgets = {
            "best_weight": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "best_reps": forms.NumberInput(attrs={"min": 0}),
            "best_duration": forms.NumberInput(attrs={"min": 0}),
            "achieved_on": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["best_weight"].required = False
        self.fields["best_reps"].required = False
        self.fields["best_duration"].required = False
        _apply_bootstrap_widgets(self)
