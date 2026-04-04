from django import forms

from ..models import AssetStatus


class AssetStatusForm(forms.ModelForm):
    class Meta:
        model = AssetStatus
        fields = [
            "name",
            "code",
            "is_active",
            "remarks",
        ]
