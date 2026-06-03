from django import forms

from ..models import ServiceType


class ServiceTypeForm(forms.ModelForm):
    class Meta:
        model = ServiceType
        fields = [
            'name',
            'code',
            'remarks',
            'is_active',
        ]
