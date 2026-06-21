from django import forms

from ..models import Subscription


class SubscriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "client" in self.fields:
            self.fields["client"].queryset = self.fields["client"].queryset.order_by("business_name", "client_code")

    class Meta:
        model = Subscription
        fields = [
            "client",
            "plan_name",
            "amount",
            "interval",
            "status",
            "period_start",
            "period_end",
        ]
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01"}),
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
        }
