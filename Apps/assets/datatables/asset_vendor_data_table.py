from core.datatables.views import BaseDataTableView
from ..models import AssetVendor


ASSET_VENDOR_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("contact_person", "contact_person"),
    ("phone_number", "phone_number"),
    ("email", "email"),
    ("address", "address"),
    ("pan_vat", "pan_vat"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class AssetVendorDataTableView(BaseDataTableView):
    model = AssetVendor
    columns = ASSET_VENDOR_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "contact_person",
        "phone_number",
        "email",
        "address",
        "pan_vat",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "code",
        "contact_person",
        "phone_number",
        "email",
        "address",
        "pan_vat",
        "is_active",
        "remarks",
    ]
