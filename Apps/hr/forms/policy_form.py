from django import forms

from ..models import Policy


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = [
            # TODO: add fields
        ]
