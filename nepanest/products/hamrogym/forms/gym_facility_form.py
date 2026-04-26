from django import forms

from ..models import GymFacility


class GymFacilityForm(forms.ModelForm):
    class Meta:
        model = GymFacility
        fields = ["name", "branch", "remarks", "is_active"]
