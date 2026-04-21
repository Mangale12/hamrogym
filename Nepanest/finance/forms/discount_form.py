from django import forms

from ..models import Discount


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = [
            "fiscal_year",
            "branch",
            "code",
            "name",
            "discount_type",
            "value",
            "scope",
        ]
