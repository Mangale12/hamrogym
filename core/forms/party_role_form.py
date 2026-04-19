from django import forms

from ..models import PartyRole


class PartyRoleForm(forms.ModelForm):
    class Meta:
        model = PartyRole
        fields = [
            "name",
            "code",
            "is_active",
            "remarks",
        ]
