from django import forms
from django.db.models import Q

from ..models import AccessRule, MembershipPlan


class AccessRuleForm(forms.ModelForm):
    class Meta:
        model = AccessRule
        fields = [
            "membership_plan",
            "rule_type",
            "time_range_start",
            "time_range_end",
            "allowed_days",
            "max_checkins_per_day",
            "branch",
            "remarks",
            "is_active",
        ]
        widgets = {
            "time_range_start": forms.TimeInput(attrs={"type": "time"}),
            "time_range_end": forms.TimeInput(attrs={"type": "time"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        plan_queryset = MembershipPlan.objects.filter(is_active=True)
        if getattr(self.instance, "membership_plan_id", None):
            plan_queryset = MembershipPlan.objects.filter(Q(is_active=True) | Q(pk=self.instance.membership_plan_id))
        self.fields["membership_plan"].queryset = plan_queryset.order_by("name")
