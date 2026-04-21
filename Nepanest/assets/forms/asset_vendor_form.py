from django import forms

from ..models import AssetVendor


class AssetVendorForm(forms.ModelForm):
    class Meta:
        model = AssetVendor
        fields = [
            # TODO: add fields
            "name",
            "code",
            "contact_person",
            "phone_number",
            "email",
            "address",
            "pan_vat",
            "is_active",
            "remarks",
        ]
