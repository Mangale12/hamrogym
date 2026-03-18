from django import forms

from ..models import ErpEntity


class ErpEntityForm(forms.ModelForm):
    class Meta:
        model = ErpEntity
        fields = [
            "name",
            "code",
            "module",
            "app_label",
            "model_name",
            "remarks",
            "is_active",
        ]
