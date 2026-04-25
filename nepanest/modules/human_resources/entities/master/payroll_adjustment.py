from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.payroll.datatables import PayrollAdjustmentDataTableView
from nepanest.modules.payroll.forms import PayrollAdjustmentForm
from nepanest.modules.payroll.models import PayrollAdjustment
from .payroll_shared import payroll_adjustment_columns


register_entity(
    EntityConfig(
        name="payroll_adjustment",
        url_path="payroll-adjustments",
        verbose_name="Payroll Adjustment",
        model=PayrollAdjustment,
        form_class=PayrollAdjustmentForm,
        datatable_view=PayrollAdjustmentDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 4, "url_name": "payroll_run_select"},
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 4, "url_name": "employee_select"},
            {"name": "salary_component", "label": "Salary Component", "type": "select", "required": False, "col": 4, "url_name": "salary_component_select"},
            {"name": "adjustment_type", "label": "Adjustment Type", "type": "static_select", "required": True, "col": 4, "options": PayrollAdjustment._meta.get_field("adjustment_type").choices},
            {"name": "amount", "label": "Amount", "type": "number", "required": True, "col": 4, "attributes": {"step": "0.01"}},
            {"name": "reason", "label": "Business Reason", "type": "textarea", "required": True, "col": 12, "placeholder": "Bonus, correction, arrear, reimbursement, or payroll recovery note."},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=payroll_adjustment_columns,
        reset_defaults={},
        select_search_fields=[
            "payroll_run__name",
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "salary_component__name",
            "adjustment_type",
        ],
    )
)
