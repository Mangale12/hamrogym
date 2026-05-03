from django import forms

from ..models import MuscleGroup


class MuscleGroupForm(forms.ModelForm):
    class Meta:
        model = MuscleGroup
        fields = [
            "name",
            "is_active",
            "remarks"
        ]
