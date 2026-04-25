from django import forms

from nepanest.modules.recruitment.models import JobPosting


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            "title",
            "job_position",
            "posting_date",
            "closing_date",
            "is_active",
            "remarks",
        ]
