from django import forms

from Nepanest.hr.models import Team


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            "organization",
            "branch",
            "department",
            "parent_team",
            "name",
            "code",
            "team_type",
            "leader",
            "start_date",
            "end_date",
            "is_active",
            "remarks",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
