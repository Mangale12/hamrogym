from django import forms

from Nepanest.hr.models import Designation


class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ["organization", "branch", "name", "level", "is_active", "remarks"]
