from django import forms

from ..models import JobBatches


class JobBatchesForm(forms.ModelForm):
    class Meta:
        model = JobBatches
        fields = [
            "hiring_plan",
            "name",
            "code",
            "branch",
            "start_date",
            "end_date",
            "status",
            "approved_by",
            "approved_at",
            "remarks",
        ]
