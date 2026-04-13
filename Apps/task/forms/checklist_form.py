from django import forms

from ..models import Checklist


class ChecklistForm(forms.ModelForm):
    class Meta:
        model = Checklist
        fields = [
            "name",
            "project_id",
            "module_id",
            "is_active",
            "remarks",
        ]
