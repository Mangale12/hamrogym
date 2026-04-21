from django import forms

from ..models import CreditPolicy


class CreditPolicyForm(forms.ModelForm):
    class Meta:
        model = CreditPolicy
        fields = [
            "fiscal_year",
            "branch",
            "name",
            "allow_over_limit",
            "over_limit_percentage",
            "block_sales",
            "is_default",
            "is_active",
            "remarks",
        ]

