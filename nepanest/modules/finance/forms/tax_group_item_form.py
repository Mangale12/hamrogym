from django import forms

from ..models import TaxGroupItem


class TaxGroupItemForm(forms.ModelForm):
    class Meta:
        model = TaxGroupItem
        fields = [
            "tax_group",
            "tax",
            "sequence",
            "override_rate",
            "is_compound",
            "is_active",
            "remarks",
        ]

