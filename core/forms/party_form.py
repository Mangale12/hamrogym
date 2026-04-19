from django import forms

from ..models import Party


class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = [
            "name",
            "display_name",
            "party_type",
            "category",
            "pan_number",
            "vat_number",
            "registration_number",
            "is_active",
            "remarks",
        ]

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ["name", "display_name", "pan_number", "vat_number", "registration_number"]:
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()
        return cleaned_data
