from django import forms

from ..models import AssetIncidentType


class AssetIncidentTypeForm(forms.ModelForm):
    class Meta:
        model = AssetIncidentType
        fields = [
            "name",
            "code",
            "require_approval",
            "auto_create_maintenance",
            "financial_impact",
            "is_active",
            "remarks"
        ]
