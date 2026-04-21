from core.config import EntityConfig
from core.registry import register_entity
from Nepanest.hr.datatables import ShiftDataTableView
from Nepanest.hr.datatables.shift_data_table import SHIFT_COLUMNS
from Nepanest.hr.forms import ShiftForm
from ...models import Shift


register_entity(
    EntityConfig(
        name="shift",
        url_path="shifts",
        verbose_name="Shift",
        model=Shift,
        form_class=ShiftForm,
        datatable_view=ShiftDataTableView,
        template_name="hr/shift_index.html",
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {
                "name" : "name",
                "label": "Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Enter shift name"
            },
            {
                "name" : "code",
                "label": "Code",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Enter shift code"
            },
            {
                "name" : "start_time",
                "label": "Start Time",
                "type": "time",
                "required": True,
                "col": 6,
                "placeholder": "Enter shift start time"
            },
            {
                "name" : "end_time",
                "label": "End Time",
                "type": "time",
                "required": True,
                "col": 6,
                "placeholder": "Enter shift end time"
            },
            {
                "name" : "break_start_time",
                "label": "Break Start Time",
                "type": "time",
                "required": True,
                "col": 6,
                "placeholder": "Enter break start time"
            },
            {
                "name" : "break_end_time",
                "label": "Break End Time",
                "type": "time",
                "required": True,
                "col": 6,
                "placeholder": "Enter break end time"
            },
            {
                "name" : "grace_start_time",
                "label": "Grace Start Time",
                "type": "time",
                "required": True,
                "col": 6,
                "placeholder": "Enter grace start time"
            },
            {
                "name" : "grace_end_time",
                "label": "Grace End Time",
                "type": "time",
                "required": True,
                "col": 6,
                "placeholder": "Enter grace end time"
            },
            {
                "name" : "is_active",
                "label": "Is Active",
                "type": "checkbox",
                "required": True,
                "col": 6,
                "placeholder": "Is the shift active?"
            },
            {
                "name" : "break_duration",
                "label": "Break Duration",
                "type": "number",
                "required": True,
                "col": 6,
                "placeholder": "Enter break duration in minutes",
                "attributes": {
                    "readonly": True
                }
            }


        ],
        datatable_columns=[
            (
                {
                    "name": key,
                    "title": "Active",
                    "render": "function(data){return data ? 'Yes' : 'No';}",
                }
                if key == "is_active"
                else {"name": key, "title": key.replace("_", " ").title()}
            )
            for key, _accessor in SHIFT_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
