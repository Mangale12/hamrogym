from django import forms

from nepanest.modules.recruitment.models import JobApplication


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
