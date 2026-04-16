from django import forms

from ..models import ChartOfAccount


class ChartOfAccountForm(forms.ModelForm):
    report_level = forms.IntegerField(required=False, disabled=True)

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

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        if parent and self.instance.pk == parent.pk:
            raise forms.ValidationError("An account head cannot be its own parent.")
        return parent
