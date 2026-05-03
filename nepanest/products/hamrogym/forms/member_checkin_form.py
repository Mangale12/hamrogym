from django import forms
from django.db.models import Q

from ..models import AccessDevice, Member, MemberCheckin, MemberMembership


class MemberCheckinForm(forms.ModelForm):
    class Meta:
        model = MemberCheckin
        fields = [
            "member",
            "member_membership",
            "checkin_time",
            "checkin_type",
            "checkout_time",
            "source",
            "device",
            "is_valid",
            "rejection_reason",
            "branch",
            "remarks",
        ]
        widgets = {
            "checkin_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "checkout_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "rejection_reason": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        member_queryset = Member.objects.all()
        if getattr(self.instance, "member_id", None):
            member_queryset = Member.objects.filter(Q(pk=self.instance.member_id) | Q(id__in=member_queryset.values("pk")))
        self.fields["member"].queryset = member_queryset.order_by("member_code")

        membership_queryset = MemberMembership.objects.all()
        if getattr(self.instance, "member_membership_id", None):
            membership_queryset = MemberMembership.objects.filter(
                Q(pk=self.instance.member_membership_id) | Q(id__in=membership_queryset.values("pk"))
            )
        self.fields["member_membership"].queryset = membership_queryset.order_by("-start_date", "-id")

        device_queryset = AccessDevice.objects.filter(is_active=True)
        if getattr(self.instance, "device_id", None):
            device_queryset = AccessDevice.objects.filter(Q(is_active=True) | Q(pk=self.instance.device_id))
        self.fields["device"].queryset = device_queryset.order_by("name")
