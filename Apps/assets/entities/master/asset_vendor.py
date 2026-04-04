from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.asset_vendor_data_table import AssetVendorDataTableView, ASSET_VENDOR_COLUMNS
from ...forms.asset_vendor_form import AssetVendorForm
from ...models import AssetVendor


register_entity(
    EntityConfig(
        name="asset_vendor",
        url_path="asset-vendors",
        verbose_name="Asset Vendor",
        model=AssetVendor,
        form_class=AssetVendorForm,
        datatable_view=AssetVendorDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "contact_person", "label": "Contact Person", "type": "text", "required": False, "col": 6},
            {"name": "phone_number", "label": "Phone Number", "type": "text", "required": False, "col": 6},
            {"name": "email", "label": "Email", "type": "email", "required": False, "col": 6},
            {"name": "address", "label": "Address", "type": "text", "required": False, "col": 12},
            {"name": "pan_vat", "label": "PAN/VAT", "type": "text", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_VENDOR_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
