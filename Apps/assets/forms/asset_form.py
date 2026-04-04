from django import forms

from Apps.assets.models.asset import AssetDocument

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
            "current_location",
            "current_department",
            "current_employee",
            "status",
            "condition",
            "is_active",
            "remarks",
        ]


class AssetDocumentForm(forms.ModelForm):
    class Meta:
        model = AssetDocument
        fields = [
            "asset",
            "document_type",
            "file_path",
        ]