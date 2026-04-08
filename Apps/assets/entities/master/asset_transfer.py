from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.asset_transfer_data_table import (
    ASSET_TRANSFER_COLUMNS,
    AssetTransferDataTableView,
)
from ...forms.asset_transfer_form import AssetTransferForm
from ...models import AssetTransfer


def _prepare_asset_transfer(request, transfer: AssetTransfer) -> None:
    asset = transfer.asset
    if not transfer.from_location_id:
        transfer.from_location = asset.current_location
    if not transfer.from_department_id:
        transfer.from_department = asset.current_department
    if not transfer.transferred_by_id:
        transfer.transferred_by = request.user


register_entity(
    EntityConfig(
        name="asset_transfer",
        url_path="asset-transfers",
        verbose_name="Asset Transfer",
        model=AssetTransfer,
        form_class=AssetTransferForm,
        datatable_view=AssetTransferDataTableView,
        fields=[
            {"name": "asset", "label": "Asset", "type": "select", "required": True, "col": 6, "url_name": "asset_select"},
            {"name": "transfer_date", "label": "Transfer Date", "type": "date", "required": True, "col": 6},
            {"name": "from_location", "label": "From Location", "type": "select", "required": False, "col": 6, "url_name": "location_select"},
            {"name": "to_location", "label": "To Location", "type": "select", "required": False, "col": 6, "url_name": "location_select"},
            {"name": "from_department", "label": "From Department", "type": "select", "required": False, "col": 6, "url_name": "department_select"},
            {"name": "to_department", "label": "To Department", "type": "select", "required": False, "col": 6, "url_name": "department_select"},
            {"name": "transferred_by", "label": "Transferred By", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
            {"name": "received_by", "label": "Received By", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_TRANSFER_COLUMNS
            if key != "id"
        ],
        pre_save=_prepare_asset_transfer,
        hide_delete_on_values=[],
        reset_defaults={},
        select_search_fields=[
            "asset__name",
            "asset__code",
            "to_location__name",
            "to_department__name",
        ],
    )
)
