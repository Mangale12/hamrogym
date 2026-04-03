from django import forms

from ..models import AssetCategory


class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = [
            "name",
            "is_active",
            "parent",
            "depreciation_applicable",
            "remarks",
        ]
