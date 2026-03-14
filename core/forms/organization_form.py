from django import forms

from core.models import Organization


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "code", "is_active", "remarks"]
