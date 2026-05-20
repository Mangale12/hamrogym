from django import forms

from ..models import LeadSource


class LeadSourceForm(forms.ModelForm):
    class Meta:
        model = LeadSource
        fields = [
            # TODO: add fields
        ]
