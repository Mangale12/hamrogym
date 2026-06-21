from django import forms

from ..models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "business_name",
            "client_code",
            "contact_email",
            "contact_phone",
            "address",
            "plan",
            "status",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }
