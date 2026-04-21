from django import forms

from ..models import JobPostingChannel


class JobPostingChannelForm(forms.ModelForm):
    class Meta:
        model = JobPostingChannel
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
