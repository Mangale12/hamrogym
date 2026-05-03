from django import forms

from ..models import Member


class CheckinSessionForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = []
