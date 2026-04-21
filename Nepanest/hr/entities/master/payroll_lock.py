from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import PayrollLockDataTableView
from ...forms.payroll_form import PayrollLockForm
from ...models import PayrollLock


register_entity(
    EntityConfig(
        name="payroll_lock",
        url_path="payroll-locks",
        verbose_name="Payroll Lock",
        model=PayrollLock,
        form_class=PayrollLockForm,
        datatable_view=PayrollLockDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 5, "url_name": "payroll_run_select"},
            {"name": "locked_by", "label": "Locked By", "type": "select", "required": False, "col": 3, "url_name": "user_select"},
            {"name": "locked_at", "label": "Locked At", "type": "datetime-local", "required": True, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "payroll_run", "title": "Payroll Run"},
            {"name": "locked_by", "title": "Locked By"},
            {"name": "locked_at", "title": "Locked At"},
            {"name": "created_at", "title": "Created At"},
        ],
        reset_defaults={"locked_at": timezone.now().strftime("%Y-%m-%dT%H:%M")},
    )
)
