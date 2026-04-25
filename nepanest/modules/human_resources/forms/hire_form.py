from django import forms

from nepanest.modules.recruitment.models import Hire


class HireForm(forms.ModelForm):
    class Meta:
        model = Hire
        fields = [
            "candidate",
            "employee",
            "hire_date",
            "designation",
            "department",
            "status",
        ]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
        }
