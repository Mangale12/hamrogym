from django import forms

from nepanest.modules.recruitment.models import SkillLevel


class SkillLevelForm(forms.ModelForm):
    class Meta:
        model = SkillLevel
        fields = [
            "name",
            "is_active",
            "remarks",
        ]
