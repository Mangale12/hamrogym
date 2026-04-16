from decimal import Decimal

from django import forms

from ..models import JournalEntry, JournalEntryStatus


class JournalEntryForm(forms.ModelForm):
    total_debit = forms.DecimalField(required=False, disabled=True, decimal_places=2, max_digits=18)
    total_credit = forms.DecimalField(required=False, disabled=True, decimal_places=2, max_digits=18)
    status = forms.ChoiceField(required=False, disabled=True, choices=JournalEntryStatus.choices)

    class Meta:
        model = JournalEntry
        fields = [
            "organization",
            "branch",
            "fiscal_year",
            "entry_no",
            "date",
            "voucher_type",
            "reference_no",
            "narration",
            "remarks",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["entry_no"].required = False
        self.fields["entry_no"].help_text = "Leave blank to auto-generate when the voucher type uses auto numbering."
        self.fields["total_debit"].initial = self.instance.total_debit or Decimal("0.00")
        self.fields["total_credit"].initial = self.instance.total_credit or Decimal("0.00")
        self.fields["status"].initial = self.instance.status or JournalEntryStatus.DRAFT

    def clean_entry_no(self):
        return (self.cleaned_data.get("entry_no") or "").strip().upper()
