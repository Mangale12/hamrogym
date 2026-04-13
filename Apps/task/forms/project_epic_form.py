from django import forms

from ..models import ProjectEpic


class ProjectEpicForm(forms.ModelForm):
    class Meta:
        model = ProjectEpic
        fields = [
            "project",
            "name",
            "description",
            "status",
            "start_date",
            "end_date",
            "priority",
            "progress",
            "is_active",
            "remarks",
        ]
