from django import forms

from Apps.account.models import ChartOfAccount

from ..models import AssetCategory


class AssetCategoryForm(forms.ModelForm):
    fixed_asset_account = forms.ModelChoiceField(
        queryset=ChartOfAccount.objects.filter(is_ledger=True, is_active=True).select_related("parent").order_by("code", "name"),
        required=False,
    )
    depreciation_expense_account = forms.ModelChoiceField(
        queryset=ChartOfAccount.objects.filter(is_ledger=True, is_active=True).select_related("parent").order_by("code", "name"),
        required=False,
    )
    accumulated_depreciation_account = forms.ModelChoiceField(
        queryset=ChartOfAccount.objects.filter(is_ledger=True, is_active=True).select_related("parent").order_by("code", "name"),
        required=False,
    )

    class Meta:
        model = AssetCategory
        fields = [
            "name",
            "is_active",
            "parent",
            "depreciation_applicable",
            "depreciation_method",
            "default_useful_life_months",
            "fixed_asset_account",
            "depreciation_expense_account",
            "accumulated_depreciation_account",
            "remarks",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label_func = lambda obj: f"{obj.code or 'AUTO'} - {obj.full_path}"
        self.fields["fixed_asset_account"].label_from_instance = label_func
        self.fields["depreciation_expense_account"].label_from_instance = label_func
        self.fields["accumulated_depreciation_account"].label_from_instance = label_func

    def clean(self):
        cleaned_data = super().clean()
        depreciation_applicable = cleaned_data.get("depreciation_applicable")
        fixed_asset_account = cleaned_data.get("fixed_asset_account")
        depreciation_expense_account = cleaned_data.get("depreciation_expense_account")
        accumulated_depreciation_account = cleaned_data.get("accumulated_depreciation_account")
        useful_life = cleaned_data.get("default_useful_life_months")

        if useful_life is not None and useful_life <= 0:
            self.add_error("default_useful_life_months", "Useful life months must be greater than zero.")

        if not depreciation_applicable:
            return cleaned_data

        if not fixed_asset_account:
            self.add_error("fixed_asset_account", "Fixed asset ledger is required when depreciation is applicable.")
        elif fixed_asset_account.account_type != "asset":
            self.add_error("fixed_asset_account", "Fixed asset ledger must be an asset account.")

        if not depreciation_expense_account:
            self.add_error("depreciation_expense_account", "Depreciation expense ledger is required when depreciation is applicable.")
        elif depreciation_expense_account.account_type != "expense":
            self.add_error("depreciation_expense_account", "Depreciation expense ledger must be an expense account.")

        if not accumulated_depreciation_account:
            self.add_error("accumulated_depreciation_account", "Accumulated depreciation ledger is required when depreciation is applicable.")
        elif accumulated_depreciation_account.account_type != "asset":
            self.add_error("accumulated_depreciation_account", "Accumulated depreciation ledger must be an asset account.")

        return cleaned_data
