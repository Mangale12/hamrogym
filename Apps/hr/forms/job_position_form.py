from django import forms

from ..models import job_position


class job_positionForm(forms.ModelForm):
    class Meta:
        model = job_position
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
