from django import forms

from ..models import ActivityLevel


class ActivityLevelForm(forms.ModelForm):
    class Meta:
        model = ActivityLevel
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
