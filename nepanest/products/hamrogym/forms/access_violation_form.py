from django import forms
from django.db.models import Q

from ..models import AccessViolation, Member, MemberMembership


class AccessViolationForm(forms.ModelForm):
    class Meta:
        model = AccessViolation
        fields = [
            "member",
            "membership",
            "violation_type",
            "detected_at",
            "action_taken",
            "branch",
            "remarks",
        ]
        widgets = {
            "detected_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "action_taken": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Member.objects.order_by("member_code")
        membership_queryset = MemberMembership.objects.all()
        if getattr(self.instance, "membership_id", None):
            membership_queryset = MemberMembership.objects.filter(
                Q(pk=self.instance.membership_id) | Q(id__in=membership_queryset.values("pk"))
            )
        self.fields["membership"].queryset = membership_queryset.order_by("-start_date", "-id")
