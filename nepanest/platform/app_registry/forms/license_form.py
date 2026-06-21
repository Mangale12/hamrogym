from django import forms

from ..models import License, LicenseRenewHistory


class LicenseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "client" in self.fields:
            self.fields["client"].queryset = self.fields["client"].queryset.order_by("business_name", "client_code")

    class Meta:
        model = License
        fields = [
            "client",
            "plan",
            "issued_on",
            "expires_on",
            "max_users",
            "max_branches",
            "grace_days",
            "is_current",
        ]
        widgets = {
            "issued_on": forms.DateInput(attrs={"type": "date"}),
            "expires_on": forms.DateInput(attrs={"type": "date"}),
        }


class LicenseRenewHistoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "license" in self.fields:
            self.fields["license"].queryset = self.fields["license"].queryset.select_related("client").order_by(
                "client__business_name",
                "-issued_on",
                "-id",
            )

    class Meta:
        model = LicenseRenewHistory
        fields = [
            "license",
            "old_expiry",
            "new_expiry",
            "renewed_by",
            "renewed_at",
            "notes",
        ]
        widgets = {
            "old_expiry": forms.DateInput(attrs={"type": "date"}),
            "new_expiry": forms.DateInput(attrs={"type": "date"}),
            "renewed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


LicenseHistoryForm = LicenseRenewHistoryForm
