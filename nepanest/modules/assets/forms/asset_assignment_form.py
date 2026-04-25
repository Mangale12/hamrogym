from django import forms
from django.utils.timezone import localdate

from ..models import AssetAssignment


class AssetAssignmentForm(forms.ModelForm):
    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        active_tab = ""
        if self.request is not None:
            active_tab = (self.request.POST.get("_active_tab") or "").strip()
        if active_tab == "return" and self.instance and self.instance.pk:
            for field_name in [
                "asset",
                "employee",
                "assigned_date",
                "expected_return_date",
                "assigned_by",
                "condition_at_issue",
            ]:
                if field_name in self.fields:
                    self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()
        active_tab = ""
        if self.request is not None:
            active_tab = (self.request.POST.get("_active_tab") or "").strip()

        if active_tab == "return":
            if self.instance and self.instance.pk:
                cleaned_data["asset"] = cleaned_data.get("asset") or self.instance.asset
                cleaned_data["employee"] = cleaned_data.get("employee") or self.instance.employee
                cleaned_data["assigned_date"] = cleaned_data.get("assigned_date") or self.instance.assigned_date
                cleaned_data["expected_return_date"] = (
                    cleaned_data.get("expected_return_date")
                    if cleaned_data.get("expected_return_date") is not None
                    else self.instance.expected_return_date
                )
                cleaned_data["assigned_by"] = cleaned_data.get("assigned_by") or self.instance.assigned_by
                cleaned_data["condition_at_issue"] = (
                    cleaned_data.get("condition_at_issue") or self.instance.condition_at_issue
                )
            cleaned_data["status"] = AssetAssignment.STATUS_RETURNED
            if not cleaned_data.get("return_date"):
                cleaned_data["return_date"] = localdate()
            if not cleaned_data.get("received_by") and self.request is not None:
                cleaned_data["received_by"] = self.request.user
        elif cleaned_data.get("status") == AssetAssignment.STATUS_ACTIVE:
            cleaned_data["return_date"] = None
            cleaned_data["received_by"] = None
            cleaned_data["condition_at_return"] = None

        return cleaned_data

    class Meta:
        model = AssetAssignment
        fields = [
            "asset",
            "employee",
            "assigned_date",
            "expected_return_date",
            "return_date",
            "assigned_by",
            "received_by",
            "condition_at_issue",
            "condition_at_return",
            "status",
            "remarks",
        ]
