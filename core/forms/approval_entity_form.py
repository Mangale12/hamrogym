from django import forms

from ..models import ApprovalEntity


class ApprovalEntityForm(forms.ModelForm):
    class Meta:
        model = ApprovalEntity
        fields = [
            # TODO: add fields
        ]
