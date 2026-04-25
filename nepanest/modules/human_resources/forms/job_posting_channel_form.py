from django import forms

from nepanest.modules.recruitment.models import JobPostingChannel


class JobPostingChannelForm(forms.ModelForm):
    class Meta:
        model = JobPostingChannel
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
