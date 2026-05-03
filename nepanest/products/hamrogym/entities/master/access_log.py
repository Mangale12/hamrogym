from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.access_log_data_table import ACCESS_LOG_COLUMNS, AccessLogDataTableView
from ...forms.access_log_form import AccessLogForm
from ...models import AccessLog


register_entity(
    EntityConfig(
        name="access_log",
        url_path="access-logs",
        verbose_name="Access Log",
        model=AccessLog,
        form_class=AccessLogForm,
        datatable_view=AccessLogDataTableView,
        fields=[
            {"name": "device", "label": "Device", "type": "select", "required": True, "col": 6, "url_name": "access_device_select"},
            {"name": "member", "label": "Member", "type": "select", "required": False, "col": 6, "url_name": "member_select"},
            {"name": "scan_time", "label": "Scan Time", "type": "datetime-local", "required": True, "col": 4},
            {"name": "processed", "label": "Processed", "type": "checkbox", "required": False, "col": 4},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "raw_data", "label": "Raw Data", "type": "textarea", "required": True, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {
                "name": key,
                "title": "Processed" if key == "processed" else key.replace("_", " ").title(),
                **({"render": "function(data){return data ? 'Yes' : 'No';}"} if key == "processed" else {}),
            }
            for key, _accessor in ACCESS_LOG_COLUMNS
            if key != "id"
        ],
        reset_defaults={"processed": False},
        select_search_fields=["device__name", "member__member_code", "raw_data"],
        select_label_func=lambda obj: f"{obj.device.name} - {obj.scan_time:%Y-%m-%d %H:%M}",
    )
)
