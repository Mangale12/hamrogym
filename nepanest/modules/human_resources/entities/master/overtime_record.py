from core.choices import APPROVAL_STATUS_CHOICES
from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.attendance.datatables import (
    OVERTIME_RECORD_COLUMNS,
    OvertimeRecordDataTableView,
)
from nepanest.modules.attendance.forms import OvertimeRecordForm
from nepanest.modules.attendance.models import OvertimeRecord


register_entity(
    EntityConfig(
        name="overtime_record",
        url_path="overtime-records",
        verbose_name="Overtime Record",
        model=OvertimeRecord,
        form_class=OvertimeRecordForm,
        datatable_view=OvertimeRecordDataTableView,
        fields=[
            {
                "name": "employee",
                "label": "Employee",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "employee_select",
            },
            {
                "name": "overtime_date",
                "label": "Overtime Date",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {
                "name": "start_time",
                "label": "Start Time",
                "type": "time",
                "required": True,
                "col": 6,
            },
            {
                "name": "end_time",
                "label": "End Time",
                "type": "time",
                "required": True,
                "col": 6,
            },
            {
                "name": "overtime_hours",
                "label": "Overtime Hours",
                "type": "number",
                "required": True,
                "col": 4,
            },
            {
                "name": "overtime_rate",
                "label": "Overtime Rate",
                "type": "number",
                "required": False,
                "col": 4,
            },
            {
                "name": "overtime_amount",
                "label": "Overtime Amount",
                "type": "number",
                "required": False,
                "col": 4,
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": APPROVAL_STATUS_CHOICES,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in OVERTIME_RECORD_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": "approved"},
        select_search_fields=[
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "status",
            "remarks",
        ],
    )
)
