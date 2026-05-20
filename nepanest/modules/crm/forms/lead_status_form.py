from django import forms

from ..models import LeadStatus


class LeadStatusForm(forms.ModelForm):
    class Meta:
        model = LeadStatus
        fields = [
            # TODO: add fields
        ]
