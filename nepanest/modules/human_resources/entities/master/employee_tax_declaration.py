from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.payroll.datatables import EmployeeTaxDeclarationDataTableView
from nepanest.modules.payroll.forms import EmployeeTaxDeclarationForm
from nepanest.modules.payroll.models import EmployeeTaxDeclaration


register_entity(
    EntityConfig(
        name="employee_tax_declaration",
        url_path="employee-tax-declarations",
        verbose_name="Employee Tax Declaration",
        model=EmployeeTaxDeclaration,
        form_class=EmployeeTaxDeclarationForm,
        datatable_view=EmployeeTaxDeclarationDataTableView,
        fields=[
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": True, "col": 6, "url_name": "fiscal_year_select"},
            {"name": "declared_amount", "label": "Declared Amount", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "investment_amount", "label": "Investment Amount", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "insurance_amount", "label": "Insurance Amount", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "other_deductions", "label": "Other Deductions", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "employee", "title": "Employee"},
            {"name": "fiscal_year", "title": "Fiscal Year"},
            {"name": "declared_amount", "title": "Declared"},
            {"name": "investment_amount", "title": "Investment"},
            {"name": "insurance_amount", "title": "Insurance"},
            {"name": "other_deductions", "title": "Other Deductions"},
            {"name": "updated_at", "title": "Updated At"},
        ],
    )
)
