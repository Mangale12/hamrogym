from django import forms
from django.db.models import Q

from ..models import AccessType, MembershipPlan


class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = [
            "name",
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
        queryset = AccessType.objects.filter(is_active=True)
        if getattr(self.instance, "access_type_id", None):
            queryset = AccessType.objects.filter(Q(is_active=True) | Q(pk=self.instance.access_type_id))
        self.fields["access_type"].queryset = queryset.order_by("name")
