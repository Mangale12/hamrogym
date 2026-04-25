from django import forms

from nepanest.modules.people.models import EmploymentType


class EmploymentTypeForm(forms.ModelForm):
    class Meta:
        model = EmploymentType
        fields = [
            "name",
            "code",
            "is_active",
            "remarks",
        ]
