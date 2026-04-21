from django import forms

from ..models import AssetCondition


class AssetConditionForm(forms.ModelForm):
    class Meta:
        model = AssetCondition
        fields = [
            "name",
            "code",
            "is_active",
            "remarks",
        ]
