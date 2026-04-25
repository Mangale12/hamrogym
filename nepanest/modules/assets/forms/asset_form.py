from django import forms

from nepanest.modules.assets.models.asset import AssetDocument

from ..models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "name",
            "code",
            "category",
            "asset_type",
            "brand",
            "model",
            "serial_number",
            "bar_code",
            "purchase_date",
            "purchase_cost",
            "vendor",
            "warranty_expiry_date",
            "use_full_life_months",
            "salvage_value",
            "depreciation_start_date",
            "current_location",
            "current_department",
            "current_employee",
            "status",
            "condition",
            "is_active",
            "remarks",
        ]

    def clean(self):
        cleaned_data = super().clean()
        purchase_cost = cleaned_data.get("purchase_cost")
        salvage_value = cleaned_data.get("salvage_value")
        useful_life = cleaned_data.get("use_full_life_months")
        purchase_date = cleaned_data.get("purchase_date")
        depreciation_start_date = cleaned_data.get("depreciation_start_date")

        if useful_life is not None and useful_life <= 0:
            self.add_error("use_full_life_months", "Use full life months must be greater than zero.")

        if purchase_cost is not None and salvage_value is not None and salvage_value > purchase_cost:
            self.add_error("salvage_value", "Salvage value cannot exceed purchase cost.")

        if purchase_date and depreciation_start_date and depreciation_start_date < purchase_date:
            self.add_error("depreciation_start_date", "Depreciation start date cannot be earlier than purchase date.")

        return cleaned_data


class AssetDocumentForm(forms.ModelForm):
    class Meta:
        model = AssetDocument
        fields = [
            "asset",
            "document_type",
            "file_path",
        ]
