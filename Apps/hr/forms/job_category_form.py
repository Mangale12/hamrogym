from django import forms

from ..models import job_category


class job_categoryForm(forms.ModelForm):
    class Meta:
        model = job_category
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
