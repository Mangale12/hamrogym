from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection

class RememberMeAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "We couldn't sign you in. Please check your username and password and try again.",
        "inactive": "This account is disabled. Please contact an administrator.",
    }

    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Enter your username",
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        )
        self.fields["remember_me"].widget.attrs.update({"id": "id_remember_me"})
