from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import PayrollApprovalDataTableView
from ...forms.payroll_form import PayrollApprovalForm
from ...models import PayrollApproval


register_entity(
    EntityConfig(
        name="payroll_approval",
        url_path="payroll-approvals",
        verbose_name="Payroll Approval",
        model=PayrollApproval,
        form_class=PayrollApprovalForm,
        datatable_view=PayrollApprovalDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 4, "url_name": "payroll_run_select"},
            {"name": "approval_level", "label": "Approval Level", "type": "number", "required": True, "col": 2, "attributes": {"min": "1"}},
            {"name": "approved_by", "label": "Approved By", "type": "select", "required": False, "col": 3, "url_name": "user_select"},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 3, "options": PayrollApproval._meta.get_field("status").choices},
            {"name": "approved_at", "label": "Approved At", "type": "datetime-local", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "payroll_run", "title": "Payroll Run"},
            {"name": "approval_level", "title": "Level"},
            {"name": "approved_by", "title": "Approved By"},
            {"name": "status", "title": "Status"},
            {"name": "approved_at", "title": "Approved At"},
            {"name": "updated_at", "title": "Updated At"},
        ],
    )
)
