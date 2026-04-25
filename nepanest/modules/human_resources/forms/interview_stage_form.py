from django import forms

from nepanest.modules.recruitment.models import InterviewStage


class InterviewStageForm(forms.ModelForm):
    class Meta:
        model = InterviewStage
        fields = [
            "name",
            "sequence",
            "is_active",
            "remarks",
        ]
