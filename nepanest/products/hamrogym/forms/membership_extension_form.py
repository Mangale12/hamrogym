from django import forms

from ..models import MembershipExtension


class MembershipExtensionForm(forms.ModelForm):
    class Meta:
        model = MembershipExtension
        fields = [
            "membership",
            "start_date",
            "end_date",
            "total_days",
            "reason",
            "approved_by"
        ]
