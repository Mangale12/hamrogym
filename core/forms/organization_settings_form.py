from django import forms
from nepanest.foundation.organization import OrganizationSettings


class OrganizationSettingsForm(forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = [
            "name",
            "registration_number",
            "pan_vat_number",
            "phone",
            "email",
            "website",
            "logo",
            "address",
            "contact_person",
            "calendar",
        ]
