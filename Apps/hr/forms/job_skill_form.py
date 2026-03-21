from django import forms

from ..models import JobSkill


class JobSkillForm(forms.ModelForm):
    class Meta:
        model = JobSkill
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
