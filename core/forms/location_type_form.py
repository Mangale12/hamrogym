from django import forms

from ..models import LocationType


class LocationTypeForm(forms.ModelForm):
    class Meta:
        model = LocationType
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
