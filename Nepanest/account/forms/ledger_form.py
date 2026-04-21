from django import forms

from ..models import ChartOfAccount, Ledger


class LedgerForm(forms.ModelForm):
    report_level = forms.IntegerField(required=False, disabled=True)
    pan_no = forms.CharField(max_length=50, required=False, label="PAN No")
    vat_no = forms.CharField(max_length=50, required=False, label="VAT No")
    contact_person = forms.CharField(max_length=150, required=False)
    mobile_no = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = ChartOfAccount
        fields = [
            "organization",
            "branch",
            "fiscal_year",
            "parent",
            "name",
            "code",
            "account_type",
            "is_depreciation",
            "sort_order",
            "is_active",
            "remarks",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].required = False
        self.fields["code"].disabled = True
        self.fields["report_level"].initial = self.instance.report_level or 1
        parent_queryset = ChartOfAccount.objects.filter(is_ledger=False).order_by("code", "name")
        if self.instance.pk:
            parent_queryset = parent_queryset.exclude(pk=self.instance.pk)
        self.fields["parent"].queryset = parent_queryset
        self.fields["parent"].label_from_instance = lambda obj: f"{obj.code or 'AUTO'} - {obj.full_path}"

        ledger_profile = getattr(self.instance, "ledger_profile", None)
        if ledger_profile:
            self.initial.setdefault("pan_no", ledger_profile.pan_no)
            self.initial.setdefault("vat_no", ledger_profile.vat_no)
            self.initial.setdefault("contact_person", ledger_profile.contact_person)
            self.initial.setdefault("mobile_no", ledger_profile.mobile_no)
            self.initial.setdefault("email", ledger_profile.email)
            self.initial.setdefault("address", ledger_profile.address)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("parent"):
            self.add_error("parent", "Parent account is required for ledger accounts.")
        return cleaned_data

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        if parent and parent.is_ledger:
            raise forms.ValidationError("Please choose a parent account group, not another ledger.")
        return parent

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance._ledger_payload = {
            "pan_no": self.cleaned_data.get("pan_no", ""),
            "vat_no": self.cleaned_data.get("vat_no", ""),
            "contact_person": self.cleaned_data.get("contact_person", ""),
            "mobile_no": self.cleaned_data.get("mobile_no", ""),
            "email": self.cleaned_data.get("email", ""),
            "address": self.cleaned_data.get("address", ""),
        }
        if commit:
            instance.save()
            Ledger.objects.update_or_create(
                chart_account=instance,
                defaults=instance._ledger_payload,
            )
            self.save_m2m()
        return instance
