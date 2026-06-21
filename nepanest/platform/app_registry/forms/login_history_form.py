from django import forms

from ..models import LoginHistory


class LoginHistoryForm(forms.ModelForm):
    class Meta:
        model = LoginHistory
        fields = [
            # TODO: add fields
        ]
