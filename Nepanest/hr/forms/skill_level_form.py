from django import forms

from ..models import SkillLevel


class SkillLevelForm(forms.ModelForm):
    class Meta:
        model = SkillLevel
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
