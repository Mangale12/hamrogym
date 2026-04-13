from django import forms

from ..models import TaskType


class TaskTypeForm(forms.ModelForm):
    class Meta:
        model = TaskType
        fields = [
            "name",
            "code",
            "sequence",
            "is_active",
            "remarks",
        ]
