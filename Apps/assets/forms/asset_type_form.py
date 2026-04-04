from django import forms

from ..models import AssetType


class AssetTypeForm(forms.ModelForm):
    class Meta:
        model = AssetType
        fields = [
            # TODO: add fields
            "name",
            "category",
            "depreciation_applicable",
            "is_active",
            "remarks",
        ]
