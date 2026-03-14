from django import forms

from ..models import leave_type


class leave_typeForm(forms.ModelForm):
    class Meta:
        model = leave_type
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
