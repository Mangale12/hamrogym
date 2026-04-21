from django import forms

from ..models import JobCategory


class JobCategoryForm(forms.ModelForm):
    class Meta:
        model = JobCategory
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
