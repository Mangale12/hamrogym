from django import forms

from ..models import AssetIncident


class AssetIncidentForm(forms.ModelForm):
    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.request and not cleaned_data.get("reported_by"):
            cleaned_data["reported_by"] = self.request.user
        return cleaned_data

    class Meta:
        model = AssetIncident
        fields = [
            "asset",
            "employee",
            "incident_type",
            "incident_date",
            "estimated_cost",
            "final_cost",
            "approval_deduction_cost",
            "reported_by",
            "approved_by",
            "fiscal_year",
            "branch",
            "status",
            "remarks",
        ]
