from django import forms

from ..models import TaxGroup


class TaxGroupForm(forms.ModelForm):
    class Meta:
        model = TaxGroup
        fields = [
            "code",
            "name",
            "application_scope",
            "is_default",
            "is_active",
            "remarks",
        ]

