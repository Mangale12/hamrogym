from django import forms

from core.models import State


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = [
            "country",
            "name",
            "code",
            "is_active",
            "remarks",
        ]
