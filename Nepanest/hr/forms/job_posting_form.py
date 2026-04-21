from django import forms

from ..models import JobPosting


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
