from django import forms

from ..models import BillingDocument


class BillingDocumentForm(forms.ModelForm):
    class Meta:
        model = BillingDocument
        fields = [
            # TODO: add fields
        ]
