from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.access_device_data_table import ACCESS_DEVICE_COLUMNS, AccessDeviceDataTableView
from ...forms.access_device_form import AccessDeviceForm
from ...models import AccessDevice


register_entity(
    EntityConfig(
        name="access_device",
        url_path="access-devices",
        verbose_name="Access Device",
        model=AccessDevice,
        form_class=AccessDeviceForm,
        datatable_view=AccessDeviceDataTableView,
        fields=[
            {"name": "name", "label": "Device Name", "type": "text", "required": True, "col": 6},
            {
                "name": "device_type",
                "label": "Device Type",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": [("", "Select Type"), *AccessDevice.DeviceType.choices],
            },
            {"name": "location", "label": "Location", "type": "text", "required": False, "col": 6},
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 3,
                "options": [("", "Select Status"), *AccessDevice.Status.choices],
            },
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 3, "url_name": "branch_select"},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {
                "name": key,
                "title": "Active" if key == "is_active" else key.replace("_", " ").title(),
                **({"render": "function(data){return data ? 'Yes' : 'No';}"} if key == "is_active" else {}),
            }
            for key, _accessor in ACCESS_DEVICE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": AccessDevice.Status.ACTIVE, "is_active": True},
        select_search_fields=["name", "device_type", "location", "status", "branch__name"],
        select_label_func=lambda obj: f"{obj.name} ({obj.get_device_type_display()})",
    )
)
