from django import forms

from Apps.hr.models import Designation


class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ["organization", "branch", "name", "level", "is_active", "remarks"]
