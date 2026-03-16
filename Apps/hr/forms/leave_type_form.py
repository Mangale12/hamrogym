from django import forms

from ..models import LeaveType


class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
