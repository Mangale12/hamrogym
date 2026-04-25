from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.payroll.datatables import EmployeeSalaryAssignmentDataTableView
from nepanest.modules.payroll.forms import EmployeeSalaryAssignmentForm
from nepanest.modules.payroll.models import EmployeeSalaryAssignment
from .payroll_shared import (
    COMPONENT_OVERRIDE_SECTION,
    employee_salary_assignment_columns,
    load_component_overrides,
    save_component_overrides,
    today,
)


register_entity(
    EntityConfig(
        name="employee_salary_assignment",
        url_path="employee-salary-assignments",
        verbose_name="Employee Salary Assignment",
        model=EmployeeSalaryAssignment,
        form_class=EmployeeSalaryAssignmentForm,
        datatable_view=EmployeeSalaryAssignmentDataTableView,
        fields=[
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "salary_structure", "label": "Salary Structure", "type": "select", "required": True, "col": 6, "url_name": "salary_structure_select"},
            {"name": "gross_salary", "label": "Gross Salary", "type": "number", "required": True, "col": 4, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "annual_ctc", "label": "Annual CTC", "type": "number", "required": False, "col": 4, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "payment_frequency", "label": "Payment Frequency", "type": "static_select", "required": True, "col": 4, "options": EmployeeSalaryAssignment._meta.get_field("payment_frequency").choices},
            {"name": "effective_from", "label": "Effective From", "type": "date", "required": True, "col": 4},
            {"name": "effective_to", "label": "Effective To", "type": "date", "required": False, "col": 4},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Optional approval note, adjustment reason, or assignment context."},
        ],
        dynamic_sections={"component_overrides": COMPONENT_OVERRIDE_SECTION},
        dynamic_sections_loader=load_component_overrides,
        dynamic_sections_saver=save_component_overrides,
        datatable_columns=employee_salary_assignment_columns,
        reset_defaults={
            "payment_frequency": "monthly",
            "effective_from": today.isoformat(),
            "is_active": True,
        },
        select_search_fields=[
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "salary_structure__name",
            "salary_structure__code",
        ],
    )
)
