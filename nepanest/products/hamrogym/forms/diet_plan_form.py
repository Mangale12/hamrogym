from django import forms

from ..models import DietPlan


class DietPlanForm(forms.ModelForm):
    class Meta:
        model = DietPlan
        fields = [
            "name",
            "fitness_goal",
            "duration_days",
            "description",
            "trainer",
            "status",
            "is_active",
            "remarks",
        ]
