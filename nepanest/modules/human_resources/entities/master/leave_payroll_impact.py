from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.payroll.datatables import LeavePayrollImpactDataTableView
from nepanest.modules.payroll.forms import LeavePayrollImpactForm
from nepanest.modules.payroll.models import LeavePayrollImpact
from .payroll_shared import leave_payroll_impact_columns


register_entity(
    EntityConfig(
        name="leave_payroll_impact",
        url_path="leave-payroll-impacts",
        verbose_name="Leave Payroll Impact",
        model=LeavePayrollImpact,
        form_class=LeavePayrollImpactForm,
        datatable_view=LeavePayrollImpactDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 4, "url_name": "payroll_run_select"},
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 4, "url_name": "employee_select"},
            {"name": "leave_request", "label": "Leave Request", "type": "select", "required": False, "col": 4, "url_name": "leave_request_select"},
            {"name": "leave_type", "label": "Leave Type", "type": "select", "required": True, "col": 4, "url_name": "leave_type_select"},
            {"name": "days", "label": "Days", "type": "number", "required": False, "col": 3},
            {"name": "is_paid", "label": "Paid Leave", "type": "checkbox", "required": False, "col": 2},
            {"name": "deduction_amount", "label": "Deduction Amount", "type": "number", "required": False, "col": 3},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=leave_payroll_impact_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "payroll_run__name",
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "leave_type__name",
        ],
    )
)
