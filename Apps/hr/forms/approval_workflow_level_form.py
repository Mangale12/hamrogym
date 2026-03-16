from django import forms

from ..models import ApprovalWorkflowLevel


class ApprovalWorkflowLevelForm(forms.ModelForm):
    class Meta:
        model = ApprovalWorkflowLevel
        fields = [
            # TODO: add fields
        ]
