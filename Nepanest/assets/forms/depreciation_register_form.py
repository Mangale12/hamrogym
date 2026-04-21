from django import forms

from ..models import AssetDepreciationRegister


class AssetDepreciationRegisterForm(forms.ModelForm):
    class Meta:
        model = AssetDepreciationRegister
        fields = [
            "asset",
            "organization",
            "branch",
            "fiscal_year",
            "schedule_month",
            "period_start",
            "period_end",
            "method",
            "life_month_index",
            "useful_life_months",
            "purchase_cost",
            "salvage_value",
            "depreciable_amount",
            "depreciation_amount",
            "opening_book_value",
            "closing_book_value",
            "fixed_asset_account",
            "depreciation_expense_account",
            "accumulated_depreciation_account",
            "status",
            "remarks",
        ]

