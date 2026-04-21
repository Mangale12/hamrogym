from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import PayrollLogDataTableView
from ...forms.payroll_form import PayrollLogForm
from ...models import PayrollLog


register_entity(
    EntityConfig(
        name="payroll_log",
        url_path="payroll-logs",
        verbose_name="Payroll Log",
        model=PayrollLog,
        form_class=PayrollLogForm,
        datatable_view=PayrollLogDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 4, "url_name": "payroll_run_select"},
            {"name": "action", "label": "Action", "type": "static_select", "required": True, "col": 3, "options": PayrollLog._meta.get_field("action").choices},
            {"name": "performed_by", "label": "Performed By", "type": "select", "required": False, "col": 5, "url_name": "user_select"},
            {"name": "old_data", "label": "Old Data", "type": "textarea", "required": False, "col": 6},
            {"name": "new_data", "label": "New Data", "type": "textarea", "required": False, "col": 6},
        ],
        datatable_columns=[
            {"name": "payroll_run", "title": "Payroll Run"},
            {"name": "action", "title": "Action"},
            {"name": "performed_by", "title": "Performed By"},
            {"name": "created_at", "title": "Created At"},
        ],
    )
)
