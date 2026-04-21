from django import forms

from ..models import LoanPolicy, LoanType


class LoanTypeForm(forms.ModelForm):
    class Meta:
        model = LoanType
        fields = [
            "name",
            "code",
            "interest_type",
            "default_interest_rate",
            "max_loan_amount",
            "max_tenure_months",
            "min_tenure_months",
            "requires_approval",
            "requires_guarantor",
            "is_active",
            "remarks",
        ]

class LoanTypePolicyForm(forms.ModelForm):
    class Meta:
        model = LoanPolicy
        fields = [
            "employment_type",
            "max_eligible_amount",
            "max_installment_amount",
            "max_tenure_months",
            "min_tenure_months",
            "interest_rate",
            "grace_period_days",
            "min_credit_score",
            "max_loan_percentage_of_salary",
            "max_emi_percentage_of_salary",
            "is_active",
            "priority",
            "remarks"
        ]
        widgets = {
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }
