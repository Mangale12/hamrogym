from django import forms

from ..models import EmployeeShift


class EmployeeShiftForm(forms.ModelForm):
    class Meta:
        model = EmployeeShift
        fields = [
            # TODO: add fields
        ]
