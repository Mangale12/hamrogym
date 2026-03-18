from django import forms

from ..models import ApprovalWorkflow


class ApprovalWorkflowForm(forms.ModelForm):
    class Meta:
        model = ApprovalWorkflow
        fields = [
            "entity",
            "name",
            "code",
            "description",
            "priority",
            "version",
            "is_default",
            "effective_from",
            "effective_to",
            "is_active",
            "remarks",
        ]
