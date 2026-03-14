from django import forms
from core.models import OrganizationSettings

class OrganizationSettingsForm(forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = ['name', 'address', 'phone', 'email']