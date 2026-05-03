from django import forms
from django.db.models import Q

from ..models import AccessType, MembershipPlan


class MembershipPlanForm(forms.ModelForm):
    TAB_FIELDS = {
        "basic": {
            "name",
            "plan_type",
            "duration_days",
            "session_limit",
            "access_type",
            "freeze_limit_days",
            "description",
            "branch",
            "remarks",
            "is_active",
        },
        "restrictions": set(),
    }

    class Meta:
        model = MembershipPlan
        fields = [
            "name",
            "plan_type",
            "duration_days",
            "session_limit",
            "access_type",
            "freeze_limit_days",
            "description",
            "branch",
            "remarks",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_tab = ((self.data.get("_active_tab") or "").strip() if self.is_bound else "") or None
        if self.active_tab:
            allowed_fields = self.TAB_FIELDS.get(self.active_tab, set())
            for name in list(self.fields.keys()):
                if name not in allowed_fields:
                    self.fields.pop(name)
        queryset = AccessType.objects.filter(is_active=True)
        if getattr(self.instance, "access_type_id", None):
            queryset = AccessType.objects.filter(Q(is_active=True) | Q(pk=self.instance.access_type_id))
        if "access_type" in self.fields:
            self.fields["access_type"].queryset = queryset.order_by("name")
