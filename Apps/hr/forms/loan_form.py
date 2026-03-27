from django import forms

from ..models import LoanAccount, LoanApplication, LoanDisbursement, LoanInstallment, LoanLedger, LoanRepayment


def _employee_label(obj):
    return f"{obj.employee_id} - {obj.full_name or obj.user.username}"


class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ["employee", "loan_type", "requested_amount", "requested_tenure", "reason", "remarks"]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 4}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = _employee_label


class LoanAccountForm(forms.ModelForm):
    class Meta:
        model = LoanAccount
        fields = [
            "loan_application",
            "employee",
            "loan_type",
            "principal_amount",
            "interest_rate",
            "interest_type",
            "tenure_months",
            "emi_amount",
            "disbursement_date",
            "start_date",
            "end_date",
            "outstanding_balance",
            "status",
            "remarks",
        ]


class LoanInstallmentForm(forms.ModelForm):
    class Meta:
        model = LoanInstallment
        fields = [
            "loan_account",
            "installment_no",
            "due_date",
            "principal_amount",
            "interest_amount",
            "total_amount",
            "paid_amount",
            "balance_amount",
            "status",
        ]


class LoanDisbursementForm(forms.ModelForm):
    class Meta:
        model = LoanDisbursement
        fields = ["loan_account", "amount", "disbursed_date", "payment_mode", "reference_no", "remarks"]


class LoanRepaymentForm(forms.ModelForm):
    class Meta:
        model = LoanRepayment
        fields = ["loan_installment", "payment_date", "amount_paid", "payment_mode", "reference_no", "remarks"]


class LoanLedgerForm(forms.ModelForm):
    class Meta:
        model = LoanLedger
        fields = ["loan_account", "transaction_type", "amount", "balance_after", "reference_id", "reference_type", "date", "remarks"]
