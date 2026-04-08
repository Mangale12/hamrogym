from django import forms

from Apps.hr.models import TeamRole


class TeamRoleForm(forms.ModelForm):
    class Meta:
        model = TeamRole
        fields = ["organization", "branch", "name", "code", "level", "is_active", "remarks"]
