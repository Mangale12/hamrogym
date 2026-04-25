from django import forms

from nepanest.modules.policies.models import Policy


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = [
            "name",
            "code",
            "module",
            "trigger_event",
            "priority",
            "effective_from",
            "effective_to",
            "is_active",
            "description",
            "remarks",
        ]
