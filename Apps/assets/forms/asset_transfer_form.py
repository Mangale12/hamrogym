from django import forms

from ..models import AssetTransfer


class AssetTransferForm(forms.ModelForm):
    class Meta:
        model = AssetTransfer
        fields = [
            "asset",
            "transfer_date",
            "from_location",
            "to_location",
            "from_department",
            "to_department",
            "transferred_by",
            "received_by",
            "remarks",
        ]
