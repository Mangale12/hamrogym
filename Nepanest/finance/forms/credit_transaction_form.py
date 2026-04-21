from django import forms

from ..models import CreditTransaction


class CreditTransactionForm(forms.ModelForm):
    class Meta:
        model = CreditTransaction
        fields = [
            "fiscal_year",
            "branch",
            "party",
            "document_type",
            "document_id",
            "transaction_date",
            "debit",
            "credit",
            "remarks",
            "is_system_generated",
        ]

