from django import forms
from django.db.models import Q

from ..models import AccessDevice, AccessLog, Member


class AccessLogForm(forms.ModelForm):
    class Meta:
        model = AccessLog
        fields = [
            "device",
            "member",
            "scan_time",
            "raw_data",
            "processed",
            "branch",
            "remarks",
        ]
        widgets = {
            "scan_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "raw_data": forms.Textarea(attrs={"rows": 4}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        device_queryset = AccessDevice.objects.filter(is_active=True)
        if getattr(self.instance, "device_id", None):
            device_queryset = AccessDevice.objects.filter(Q(is_active=True) | Q(pk=self.instance.device_id))
        self.fields["device"].queryset = device_queryset.order_by("name")
        self.fields["member"].queryset = Member.objects.order_by("member_code")
