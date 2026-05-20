from django import forms

from ..models import GymClass


class GymClassForm(forms.ModelForm):
    class Meta:
        model = GymClass
        fields = [
            "name",
            "class_type",
            "difficulty_level",
            "max_capacity",
            "duration_minutes",
            "trainer",
            "is_active",
            "remarks",
        ]
