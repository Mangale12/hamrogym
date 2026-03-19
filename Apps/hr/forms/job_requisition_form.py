from django import forms

from ..models import JobRequisition


class JobRequisitionForm(forms.ModelForm):
    class Meta:
        model = JobRequisition
        fields = [
            "__all__"
        ]
