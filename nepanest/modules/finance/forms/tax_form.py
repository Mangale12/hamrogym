from django import forms

from ..models import Tax


class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = [
            "code",
            "name",
            "tax_type",
            "calculation_method",
            "application_scope",
            "rate",
            "fixed_amount",
            "effective_from",
            "effective_to",
            "is_inclusive",
            "is_recoverable",
            "is_active",
            "remarks",
        ]
        widgets = {
            "effective_from": forms.DateInput(attrs={"type": "date"}),
            "effective_to": forms.DateInput(attrs={"type": "date"}),
        }

