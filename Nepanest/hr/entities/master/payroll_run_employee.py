from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import PayrollRunEmployeeDataTableView
from ...forms.payroll_form import PayrollRunEmployeeForm
from ...models import PayrollRunEmployee
from .payroll_shared import payroll_run_employee_columns


register_entity(
    EntityConfig(
        name="payroll_run_employee",
        url_path="payroll-run-employees",
        verbose_name="Payroll Run Employee",
        model=PayrollRunEmployee,
        form_class=PayrollRunEmployeeForm,
        datatable_view=PayrollRunEmployeeDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 6, "url_name": "payroll_run_select"},
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "employee_salary_assignment", "label": "Salary Assignment", "type": "select", "required": True, "col": 6, "url_name": "employee_salary_assignment_select"},
            {"name": "salary_structure_name", "label": "Salary Structure", "type": "text", "required": False, "col": 6},
            {"name": "gross_salary", "label": "Gross Salary", "type": "number", "required": False, "col": 4},
            {"name": "gross_earnings", "label": "Gross Earnings", "type": "number", "required": False, "col": 4},
            {"name": "total_deductions", "label": "Total Deductions", "type": "number", "required": False, "col": 4},
            {"name": "employer_contributions", "label": "Employer Contributions", "type": "number", "required": False, "col": 4},
            {"name": "taxable_income", "label": "Taxable Income", "type": "number", "required": False, "col": 4},
            {"name": "income_tax", "label": "Income Tax", "type": "number", "required": False, "col": 4},
            {"name": "net_salary", "label": "Net Salary", "type": "number", "required": False, "col": 4},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 4, "options": PayrollRunEmployee._meta.get_field("status").choices},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=payroll_run_employee_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "payroll_run__name",
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "status",
        ],
    )
)
