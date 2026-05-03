from django import forms
from django.db.models import Q

from ..models import Member, MemberMembership, MembershipPlan, MembershipFreeze


class MemberMembershipForm(forms.ModelForm):
    class Meta:
        model = MemberMembership
        fields = [
            "member",
            "membership_plan",
            "start_date",
            "end_date",
            "total_sessions",
            "used_sessions",
            "status",
            "source",
            "notes",
            "branch",
            "remarks",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        member_queryset = Member.objects.all()
        if getattr(self.instance, "member_id", None):
            member_queryset = Member.objects.filter(Q(pk=self.instance.member_id) | Q(id__in=member_queryset.values("pk")))
        self.fields["member"].queryset = member_queryset.order_by("member_code")

        plan_queryset = MembershipPlan.objects.filter(is_active=True)
        if getattr(self.instance, "membership_plan_id", None):
            plan_queryset = MembershipPlan.objects.filter(
                Q(is_active=True) | Q(pk=self.instance.membership_plan_id)
            )
        self.fields["membership_plan"].queryset = plan_queryset.order_by("name")


class MembershipFreezeForm(forms.ModelForm):
    class Meta:
        model = MembershipFreeze
        fields = [
            "member",
            "membership",
            "start_date",
            "end_date",
            "total_days",
            "reason",
            "approved_by",
            "branch",
            "remarks",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        member_queryset = Member.objects.all()
        if getattr(self.instance, "member_id", None):
            member_queryset = Member.objects.filter(Q(pk=self.instance.member_id) | Q(id__in=member_queryset.values("pk")))
        self.fields["member"].queryset = member_queryset.order_by("member_code")

        membership_queryset = MemberMembership.objects.all()
        if getattr(self.instance, "membership_id", None):
            membership_queryset = MemberMembership.objects.filter(
                Q(pk=self.instance.membership_id) | Q(id__in=membership_queryset.values("pk"))
            )
        self.fields["membership"].queryset = membership_queryset.order_by("-start_date", "-id")
