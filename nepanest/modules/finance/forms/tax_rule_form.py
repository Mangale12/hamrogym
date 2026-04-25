from django import forms

from ..models import TaxRule


class TaxRuleForm(forms.ModelForm):
    class Meta:
        model = TaxRule
        fields = [
            "code",
            "name",
            "tax",
            "rule_type",
            "application_scope",
            "party_type",
            "country",
            "min_amount",
            "max_amount",
            "priority",
            "stop_processing",
            "is_active",
            "remarks",
        ]
