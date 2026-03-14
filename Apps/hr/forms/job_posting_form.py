from django import forms

from ..models import JobPosting


class job_postingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            # TODO: add fields
            "job_position",
            "posting_date",
            "closing_date",
            "is_active",
            "remarks",
        ]
