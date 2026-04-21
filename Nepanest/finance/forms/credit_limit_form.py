from decimal import Decimal

from django import forms

from ..models import CreditLimit


class CreditLimitForm(forms.ModelForm):
    used_credit = forms.DecimalField(required=False, disabled=True, decimal_places=2, max_digits=14)
    available_credit = forms.DecimalField(required=False, disabled=True, decimal_places=2, max_digits=14)

    class Meta:
        model = CreditLimit
        fields = [
            "fiscal_year",
            "branch",
            "party",
            "policy",
            "credit_limit",
            "remarks",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        used_credit = self.instance.used_credit if self.instance and self.instance.pk else Decimal("0.00")
        available_credit = (
            self.instance.available_credit if self.instance and self.instance.pk else self.instance.credit_limit or Decimal("0.00")
        )
        self.fields["used_credit"].initial = used_credit
        self.fields["available_credit"].initial = available_credit

