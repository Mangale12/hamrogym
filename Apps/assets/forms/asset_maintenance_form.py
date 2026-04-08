from django import forms

from ..models import AssetMaintenanceRecord


class AssetMaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = AssetMaintenanceRecord
        fields = [
            "asset",
            "incident",
            "maintenance_date",
            "maintenance_type",
            "vendor",
            "cost",
            "performed_by",
            "status",
            "remarks",
        ]
