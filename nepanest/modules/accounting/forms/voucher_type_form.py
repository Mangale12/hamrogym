from django import forms

from ..models import VoucherType


class VoucherTypeForm(forms.ModelForm):
    class Meta:
        model = VoucherType
        fields = [
            "organization",
            "branch",
            "name",
            "code",
            "category",
            "nature",
            "affects_cash",
            "affects_bank",
            "auto_numbering",
            "prefix",
            "last_number",
            "requires_reference",
            "requires_approval",
            "allow_negative",
            "is_system_generated",
            "is_active",
            "description",
        ]

    def clean_code(self):
        return (self.cleaned_data.get("code") or "").strip().upper()

    def clean_prefix(self):
        return (self.cleaned_data.get("prefix") or "").strip().upper()
