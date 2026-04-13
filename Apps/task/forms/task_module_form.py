from django import forms

from ..models import TaskModule


class TaskModuleForm(forms.ModelForm):
    class Meta:
        model = TaskModule
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
