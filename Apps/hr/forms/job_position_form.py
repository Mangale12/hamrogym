from django import forms

from ..models import JobPosition


class JobPositionForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = [
            "name",
            "department",
            "designation",
            "job_category",
            "vacancies",
            "description",
            "employeement_type",
            "salary_min",
            "salary_max",
            "is_active",
            "remarks",
        ]
