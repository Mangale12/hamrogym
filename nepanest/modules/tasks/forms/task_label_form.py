from django import forms

from ..models import TaskLabel


class TaskLabelForm(forms.ModelForm):
    class Meta:
        model = TaskLabel
        fields = [
            "name",
            "code",
            "color",
            "sequence",
            "is_active",
            "remarks",
            "branch",
            "fiscal_year",
            "organization"
        ]
