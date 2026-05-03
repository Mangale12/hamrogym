from django import forms

from ..models import AccessDevice


class AccessDeviceForm(forms.ModelForm):
    class Meta:
        model = AccessDevice
        fields = [
            "name",
            "device_type",
            "location",
            "status",
            "branch",
            "remarks",
            "is_active",
        ]
        widgets = {
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }
