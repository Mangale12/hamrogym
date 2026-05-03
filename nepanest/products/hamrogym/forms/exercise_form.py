from django import forms

from ..models import Exercise


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = [
            # TODO: add fields
            "name",
            "muscle_group",
            "equipment_type",
            "exercise_type",
            "difficulty_level",
            "instructions",
            "precautions",
            "is_active",
            "remarks"
        ]
