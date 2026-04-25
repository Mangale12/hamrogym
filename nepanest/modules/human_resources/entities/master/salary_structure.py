from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.payroll.datatables import SalaryStructureDataTableView
from nepanest.modules.payroll.forms import SalaryStructureForm
from nepanest.modules.payroll.models import SalaryStructure
from .payroll_shared import (
    STRUCTURE_COMPONENT_SECTION,
    load_structure_components,
    salary_structure_columns,
    save_structure_components,
    today,
)


register_entity(
    EntityConfig(
        name="salary_structure",
        url_path="salary-structures",
        verbose_name="Salary Structure",
        model=SalaryStructure,
        form_class=SalaryStructureForm,
        datatable_view=SalaryStructureDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "required": False, "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "currency", "label": "Currency", "type": "select", "required": False, "col": 4, "url_name": "currency_select"},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 3, "placeholder": "SAL-STD-01"},
            {"name": "name", "label": "Structure Name", "type": "text", "required": True, "col": 5, "placeholder": "Monthly Staff Structure"},
            {"name": "effective_from", "label": "Effective From", "type": "date", "required": True, "col": 2},
            {"name": "effective_to", "label": "Effective To", "type": "date", "required": False, "col": 2},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12, "placeholder": "Describe which employees or salary policy this structure is meant for."},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 8, "placeholder": "Optional implementation note or approval note."},
        ],
        dynamic_sections={"structure_components": STRUCTURE_COMPONENT_SECTION},
        dynamic_sections_loader=load_structure_components,
        dynamic_sections_saver=save_structure_components,
        datatable_columns=salary_structure_columns,
        reset_defaults={"effective_from": today.isoformat(), "is_active": True},
    )
)
