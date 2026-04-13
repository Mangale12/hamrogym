from django import forms

from ..models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "code",
            "module",
            "manager",
            "description",
            "status",
            "priority",
            "start_date",
            "end_date",
            "is_active",
            "remarks",
        ]
