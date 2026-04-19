from django import forms

from ..models import PartyType


class PartyTypeForm(forms.ModelForm):
    class Meta:
        model = PartyType
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
