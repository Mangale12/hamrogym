from django import forms

from Apps.hr.models import Department


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["organization", "branch", "name", "code", "is_active", "remarks"]
