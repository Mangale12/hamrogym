from django import forms

from ..models import EquipmentType


class EquipmentTypeForm(forms.ModelForm):
    class Meta:
        model = EquipmentType
        fields = [
            'name',
            'remarks',
            'is_active',
        ]
