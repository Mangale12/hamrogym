from django import forms

from nepanest.modules.people.models import Designation


class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ["organization", "branch", "name", "level", "is_active", "remarks"]
