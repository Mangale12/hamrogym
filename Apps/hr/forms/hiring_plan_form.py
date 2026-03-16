from django import forms

from ..models import HiringPlan


class HiringPlanForm(forms.ModelForm):
    class Meta:
        model = HiringPlan
        fields = [
            # TODO: add fields
        ]
