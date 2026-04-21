from django import forms

from ..models import JobApplication


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            "applicant",
            "job_posting",
            "status",
            "is_active",
            "remarks",
        ]
