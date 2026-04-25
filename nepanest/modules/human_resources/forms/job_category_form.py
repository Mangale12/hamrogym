from django import forms

from nepanest.modules.recruitment.models import JobCategory


class JobCategoryForm(forms.ModelForm):
    class Meta:
        model = JobCategory
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
