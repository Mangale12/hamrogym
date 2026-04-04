from django import forms

from core.models import Location


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            "location_type",
            "name",
            "code",
            "is_active",
            "remarks",
        ]
