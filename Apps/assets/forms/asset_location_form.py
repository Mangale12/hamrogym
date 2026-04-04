from django import forms

from ..models import AssetLocation


class AssetLocationForm(forms.ModelForm):
    class Meta:
        model = AssetLocation
        fields = [
            # TODO: add fields
            "name",
            "branch",
            "address",
            "is_active",
            "remarks",
        ]
