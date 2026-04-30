from django import forms
from django.db.models import Q

from ..models import Member, MemberReferral


class MemberReferralForm(forms.ModelForm):
    class Meta:
        model = MemberReferral
        fields = [
            "referrer_member",
            "referred_member",
            "referral_date",
            "branch",
            "notes",
        ]
        widgets = {
            "referral_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        member_queryset = Member.objects.all()
        if self.instance.pk:
            member_queryset = Member.objects.filter(
                Q(is_active=True)
                | Q(pk=self.instance.referrer_member_id)
                | Q(pk=self.instance.referred_member_id)
            )
        else:
            member_queryset = member_queryset.filter(is_active=True)

        self.fields["referrer_member"].queryset = member_queryset.order_by("member_code")
        self.fields["referred_member"].queryset = member_queryset.order_by("member_code")

    def clean_notes(self):
        return (self.cleaned_data.get("notes") or "").strip()
