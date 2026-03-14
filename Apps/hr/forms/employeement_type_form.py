from django import forms

from ..models import employeement_type


class employeement_typeForm(forms.ModelForm):
    class Meta:
        model = employeement_type
        fields = [
            "name",
            "code",
            "is_active",
            "remarks",
        ]
