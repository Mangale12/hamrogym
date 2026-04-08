from django import forms

from ..models import TaskStatus


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = TaskStatus
        fields = [
            # TODO: add fields
        ]
