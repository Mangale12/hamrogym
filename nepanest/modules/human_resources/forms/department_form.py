from django import forms

from nepanest.modules.people.models import Department


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["organization", "branch", "name", "code", "is_active", "remarks"]
