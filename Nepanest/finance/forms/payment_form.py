from decimal import Decimal

from django import forms

from ..models import Payment, PaymentStatus


class PaymentForm(forms.ModelForm):
    allocated_amount = forms.DecimalField(required=False, disabled=True, decimal_places=2, max_digits=14)
    unapplied_amount = forms.DecimalField(required=False, disabled=True, decimal_places=2, max_digits=14)
    status = forms.ChoiceField(required=False, disabled=True, choices=PaymentStatus.choices)

    class Meta:
        model = Payment
        fields = [
            "organization",
            "branch",
            "fiscal_year",
            "payment_no",
            "reference",
            "reference_date",
            "date",
            "payment_type",
            "party",
            "billing_profile",
            "payment_method",
            "currency",
            "exchange_rate",
            "amount",
            "journal_entry",
            "remarks",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_no"].required = False
        self.fields["payment_no"].help_text = "Leave blank to auto-generate a payment number."
        self.fields["billing_profile"].required = False
        self.fields["party"].required = False
        self.fields["reference"].required = False
        self.fields["reference_date"].required = False
        self.fields["journal_entry"].required = False
        self.fields["exchange_rate"].initial = self.instance.exchange_rate or Decimal("1.000000")
        self.fields["allocated_amount"].initial = self.instance.allocated_amount or Decimal("0.00")
        self.fields["unapplied_amount"].initial = self.instance.unapplied_amount or self.instance.amount or Decimal("0.00")
        self.fields["status"].initial = self.instance.status or PaymentStatus.DRAFT

    def clean_payment_no(self):
        return (self.cleaned_data.get("payment_no") or "").strip().upper()

    def clean_reference(self):
        return (self.cleaned_data.get("reference") or "").strip()

