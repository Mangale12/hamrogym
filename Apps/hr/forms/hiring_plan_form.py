from django import forms

from ..models import HiringPlan


class HiringPlanForm(forms.ModelForm):
    class Meta:
        model = HiringPlan
        fields = [
            "name",
            "code",
            "description",
            "status",
            "is_active",
            "remarks",
        ]
