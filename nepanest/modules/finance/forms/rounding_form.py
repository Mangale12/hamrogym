from django import forms

from ..models import Rounding


class RoundingForm(forms.ModelForm):
    class Meta:
        model = Rounding
        fields = [
            "fiscal_year",
            "branch",
            "code",
            "name",
            "application_scope",
            "rounding_method",
            "round_on",
            "precision",
            "increment",
            "is_cash_rounding",
            "is_default",
            "is_active",
            "remarks",
        ]

