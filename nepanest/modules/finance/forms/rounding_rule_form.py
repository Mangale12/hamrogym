from django import forms

from ..models import RoundingRule


class RoundingRuleForm(forms.ModelForm):
    class Meta:
        model = RoundingRule
        fields = [
            "fiscal_year",
            "branch",
            "name",
            "rounding",
            "application_scope",
            "document_type",
            "party_type",
            "currency",
            "payment_method",
            "min_amount",
            "max_amount",
            "priority",
            "stop_processing",
            "is_active",
            "remarks",
        ]

