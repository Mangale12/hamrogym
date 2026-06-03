from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.lead_status_data_table import LeadStatusDataTableView, LEAD_STATUS_COLUMNS
from ...forms.lead_status_form import LeadStatusForm
from ...models import LeadStatus


register_entity(
    EntityConfig(
        name="lead_status",
        url_path="lead-statuses",
        verbose_name="Lead Status",
        model=LeadStatus,
        form_class=LeadStatusForm,
        datatable_view=LeadStatusDataTableView,
        template_name="crm/entity_index.html",
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 4},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": False, "col": 4},
            {
                "name": "color",
                "label": "Color",
                "type": "color",
                "required": True,
                "col": 4,
                "class": "form-control form-control-color",
                "attributes": {"title": "Choose status color"},
            },
            {"name": "is_default", "label": "Is Default", "type": "checkbox", "required": False, "col": 4},
            {"name": "is_closed", "label": "Is Closed", "type": "checkbox", "required": False, "col": 4},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {
                "name": key,
                "title": key.replace("_", " ").title(),
                **(
                    {
                        "render": (
                            "function(data){"
                            "const color=data||'#3498DB';"
                            "return `<div class=\"d-flex align-items-center gap-2\">` +"
                            "`<span style=\"width:14px;height:14px;border-radius:999px;display:inline-block;border:1px solid rgba(15,23,42,.12);background:${color};\"></span>` +"
                            "`<span>${color}</span></div>`;"
                            "}"
                        )
                    }
                    if key == "color"
                    else {
                        "render": "function(data){return data ? 'Yes' : 'No';}"
                    }
                    if key in {"is_default", "is_active", "is_closed"}
                    else {}
                ),
            }
            for key, _accessor in LEAD_STATUS_COLUMNS
            if key != "id"
        ],
        reset_defaults={"sequence": 0, "color": "#3498DB", "is_active": True},
    )
)
