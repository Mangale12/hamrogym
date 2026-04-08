from django.core.exceptions import ValidationError

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.asset_maintenance_data_table import (
    ASSET_MAINTENANCE_COLUMNS,
    AssetMaintenanceRecordDataTableView,
)
from ...forms.asset_maintenance_form import AssetMaintenanceRecordForm
from ...models import AssetMaintenanceRecord


def _prepare_asset_maintenance(request, maintenance: AssetMaintenanceRecord) -> None:
    if not maintenance.performed_by_id:
        maintenance.performed_by = request.user


def _start_maintenance(request, maintenance: AssetMaintenanceRecord):
    if maintenance.status != AssetMaintenanceRecord.STATUS_PENDING:
        raise ValidationError("Only pending maintenance records can be started.")
    maintenance.status = AssetMaintenanceRecord.STATUS_IN_PROGRESS
    if not maintenance.performed_by_id:
        maintenance.performed_by = request.user
    maintenance.save(update_fields=["status", "performed_by", "updated_at"])
    return {"message": "Maintenance started successfully."}


def _complete_maintenance(request, maintenance: AssetMaintenanceRecord):
    if maintenance.status not in {
        AssetMaintenanceRecord.STATUS_PENDING,
        AssetMaintenanceRecord.STATUS_IN_PROGRESS,
    }:
        raise ValidationError("Only pending or in-progress maintenance records can be completed.")
    maintenance.status = AssetMaintenanceRecord.STATUS_COMPLETED
    if not maintenance.performed_by_id:
        maintenance.performed_by = request.user
    maintenance.save(update_fields=["status", "performed_by", "updated_at"])
    return {"message": "Maintenance completed successfully."}


register_entity(
    EntityConfig(
        name="asset_maintenance",
        url_path="asset-maintenance",
        verbose_name="Asset Maintenance",
        model=AssetMaintenanceRecord,
        form_class=AssetMaintenanceRecordForm,
        datatable_view=AssetMaintenanceRecordDataTableView,
        fields=[
            {"name": "asset", "label": "Asset", "type": "select", "required": True, "col": 6, "url_name": "asset_select"},
            {"name": "incident", "label": "Incident", "type": "select", "required": False, "col": 6, "url_name": "asset_incident_select"},
            {"name": "maintenance_date", "label": "Maintenance Date", "type": "date", "required": True, "col": 4},
            {"name": "maintenance_type", "label": "Maintenance Type", "type": "text", "required": True, "col": 4},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 4, "options": AssetMaintenanceRecord.STATUS_CHOICES},
            {"name": "vendor", "label": "Vendor", "type": "select", "required": False, "col": 4, "url_name": "asset_vendor_select"},
            {"name": "cost", "label": "Cost", "type": "number", "required": False, "col": 4},
            {"name": "performed_by", "label": "Performed By", "type": "select", "required": False, "col": 4, "url_name": "user_select"},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_MAINTENANCE_COLUMNS
            if key != "id"
        ],
        pre_save=_prepare_asset_maintenance,
        row_actions={
            "start": _start_maintenance,
            "complete": _complete_maintenance,
        },
        action_state_field="status",
        hide_edit_on_values=[AssetMaintenanceRecord.STATUS_COMPLETED],
        hide_delete_on_values=[AssetMaintenanceRecord.STATUS_COMPLETED],
        reset_defaults={"status": AssetMaintenanceRecord.STATUS_PENDING},
        action_buttons=[
            {
                "action_name": "start",
                "title": "Start",
                "icon_class": "fas fa-play",
                "class_name": "btn-outline-primary",
                "confirm_text": "Start this maintenance record?",
                "success_message": "Maintenance started successfully.",
                "hide_on_values": [
                    AssetMaintenanceRecord.STATUS_IN_PROGRESS,
                    AssetMaintenanceRecord.STATUS_COMPLETED,
                ],
            },
            {
                "action_name": "complete",
                "title": "Complete",
                "icon_class": "fas fa-check",
                "class_name": "btn-outline-success",
                "confirm_text": "Mark this maintenance as completed?",
                "success_message": "Maintenance completed successfully.",
                "hide_on_values": [AssetMaintenanceRecord.STATUS_COMPLETED],
            },
        ],
        select_search_fields=[
            "asset__name",
            "asset__code",
            "incident__incident_type__name",
            "maintenance_type",
            "status",
        ],
    )
)
