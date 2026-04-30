from django import forms

from ..models import AccessType


class AccessTypeForm(forms.ModelForm):
    class Meta:
        model = AccessType
        fields = ["name", "code", "description", "branch", "remarks", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }
