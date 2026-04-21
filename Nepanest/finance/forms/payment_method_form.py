from django import forms

from ..models import PaymentMethod


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = [
            "code",
            "name",
            "category",
            "provider",
            "sequence",
            "is_digital",
            "supports_online",
            "supports_qr",
            "requires_reference",
            "is_default",
            "is_active",
            "remarks",
        ]
