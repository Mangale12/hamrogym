from django import forms

from ..models import TaskStatus


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = TaskStatus
        fields = [
            "name",
            "code",
            "badge_color",
            "sequence",
            "is_default",
            "is_closed",
            "is_cancelled",
        ]
