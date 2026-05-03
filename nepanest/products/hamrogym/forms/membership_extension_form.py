from django import forms

from ..models import MembershipExtension


class MembershipExtensionForm(forms.ModelForm):
    class Meta:
        model = MembershipExtension
        fields = [
            "membership",
            "extra_days",
            "reason",
            "approved_by"
        ]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 3}),
        }
