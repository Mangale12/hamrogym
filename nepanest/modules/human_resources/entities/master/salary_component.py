from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.payroll.datatables import SalaryComponentDataTableView
from nepanest.modules.payroll.forms import SalaryComponentForm
from nepanest.modules.payroll.models import SalaryComponent
from .payroll_shared import salary_component_columns


register_entity(
    EntityConfig(
        name="salary_component",
        url_path="salary-components",
        verbose_name="Salary Component",
        model=SalaryComponent,
        form_class=SalaryComponentForm,
        datatable_view=SalaryComponentDataTableView,
        fields=[
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 3, "placeholder": "BASIC"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 5, "placeholder": "Basic Salary"},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": True, "col": 2},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 2},
            {"name": "component_type", "label": "Component Type", "type": "static_select", "required": True, "col": 4, "options": SalaryComponent._meta.get_field("component_type").choices},
            {"name": "value_type", "label": "Value Type", "type": "static_select", "required": True, "col": 4, "options": SalaryComponent._meta.get_field("value_type").choices},
            {"name": "tax_treatment", "label": "Tax Treatment", "type": "static_select", "required": True, "col": 4, "options": SalaryComponent._meta.get_field("tax_treatment").choices},
            {"name": "affects_gross", "label": "Affects Gross", "type": "checkbox", "required": False, "col": 4},
            {"name": "affects_net", "label": "Affects Net", "type": "checkbox", "required": False, "col": 4},
            {"name": "is_statutory", "label": "Statutory", "type": "checkbox", "required": False, "col": 4},
            {"name": "formula_expression", "label": "Formula Expression", "type": "textarea", "required": False, "col": 12, "placeholder": "Example: BASIC * 0.10 or GROSS * 0.40"},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Optional implementation notes or compliance notes."},
        ],
        datatable_columns=salary_component_columns,
        reset_defaults={
            "sequence": 1,
            "is_active": True,
            "affects_gross": True,
            "affects_net": True,
        },
    )
)
