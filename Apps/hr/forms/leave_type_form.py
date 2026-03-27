from django import forms

from ..models import LeaveType
from ..models import LeavePolicy

class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = [
            "name",
            "is_paid",
            "is_carry_forward",
            "is_encashable",
            "requires_attachment",
            "requires_approval",
            "max_days_per_year",
            "color",
            "description",
            "is_active",
            "remarks",
        ]


class LeavePolicyForm(forms.ModelForm):
    class Meta:
        model = LeavePolicy
        fields = [
            "leave_type",
            "employment_type",
            "days_allowed",
            "accrual_type",
            "accrual_rate",
            "carry_forward_limit",
            "carry_forward_expiry_days",
            "max_consecutive_days",
            "min_service_days",
            "allow_half_day",
            "allow_negative_balance",
            "effective_from",
            "effective_to",
            "is_active",
            "remarks",
        ]