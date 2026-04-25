from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.payroll.datatables import PayslipDataTableView
from nepanest.modules.payroll.forms import PayslipForm
from nepanest.modules.payroll.models import Payslip


register_entity(
    EntityConfig(
        name="payslip",
        url_path="payslips",
        verbose_name="Payslip",
        model=Payslip,
        form_class=PayslipForm,
        datatable_view=PayslipDataTableView,
        fields=[
            {"name": "payroll_run_employee", "label": "Payroll Employee", "type": "select", "required": True, "col": 6, "url_name": "payroll_run_employee_select"},
            {"name": "payslip_number", "label": "Payslip Number", "type": "text", "required": True, "col": 3, "placeholder": "PS-2026-0001"},
            {"name": "generated_date", "label": "Generated Date", "type": "date", "required": True, "col": 3},
            {"name": "file_path", "label": "File Path", "type": "text", "required": False, "col": 9, "placeholder": "media/payslips/ps-2026-0001.pdf"},
            {"name": "email_sent", "label": "Email Sent", "type": "checkbox", "required": False, "col": 3},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "payroll_run_employee", "title": "Payroll Employee"},
            {"name": "payslip_number", "title": "Payslip Number"},
            {"name": "generated_date", "title": "Generated Date"},
            {"name": "file_path", "title": "File Path"},
            {"name": "email_sent", "title": "Email Sent", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "updated_at", "title": "Updated At"},
        ],
        reset_defaults={"generated_date": timezone.localdate().isoformat()},
    )
)
