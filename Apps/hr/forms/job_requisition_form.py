from django import forms

from ..models import JobRequisition


class JobRequisitionForm(forms.ModelForm):
    class Meta:
        model = JobRequisition
        fields = [
            "batch",
            "requisition_code",
            "branch",
            "department",
            "designation",
            "employment_type",
            "requested_by",
            "vacancies",
            "job_title",
            "job_description",
            "job_responsibilities",
            "required_skills",
            "required_experience",
            "education_requirement",
            "salary_min",
            "salary_max",
            "job_location",
            "priority",
            "expected_joining_date",
            "recruitment_reason",
            "status",
            "remarks"
        ]
