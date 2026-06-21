from django import forms

from ..models import TenantDB


class TenantDBForm(forms.ModelForm):
    class Meta:
        model = TenantDB
        fields = [
            "client",
            "db_name",
            "db_user",
            "db_password",
            "db_host",
            "db_port",
            "status",
        ]
        widgets = {
            "db_password": forms.PasswordInput(render_value=True),
        }
