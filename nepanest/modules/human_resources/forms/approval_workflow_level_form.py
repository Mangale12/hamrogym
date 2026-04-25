from django import forms

from nepanest.modules.recruitment.models import ApprovalWorkflowLevel


class ApprovalWorkflowLevelForm(forms.ModelForm):
    class Meta:
        model = ApprovalWorkflowLevel
        fields = [
            # TODO: add fields
        ]
