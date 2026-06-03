from django import forms

from ..models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "name",
            "code",
            "service_type",
            "default_price",
            "is_active",
            "remarks",
        ]
