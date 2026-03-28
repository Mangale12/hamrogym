from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import PayrollSettingDataTableView
from ...forms.payroll_form import PayrollSettingForm
from ...models import PayrollSetting


register_entity(
    EntityConfig(
        name="payroll_setting",
        url_path="payroll-settings",
        verbose_name="Payroll Setting",
        model=PayrollSetting,
        form_class=PayrollSettingForm,
        datatable_view=PayrollSettingDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "required": False, "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "default_working_days", "label": "Default Working Days", "type": "number", "required": True, "col": 4, "attributes": {"min": "1", "max": "31"}},
            {"name": "overtime_calculation_method", "label": "Overtime Method", "type": "static_select", "required": True, "col": 4, "options": PayrollSetting._meta.get_field("overtime_calculation_method").choices},
            {"name": "rounding_method", "label": "Rounding Method", "type": "static_select", "required": True, "col": 4, "options": PayrollSetting._meta.get_field("rounding_method").choices},
            {"name": "adjustment_reference_type", "label": "Reference Type", "type": "static_select", "required": True, "col": 4, "options": PayrollSetting._meta.get_field("adjustment_reference_type").choices},
            {"name": "tax_deduction_component", "label": "Tax Component", "type": "select", "required": False, "col": 4, "url_name": "salary_component_select"},
            {"name": "provident_fund_employee_component", "label": "PF Employee Component", "type": "select", "required": False, "col": 4, "url_name": "salary_component_select"},
            {"name": "provident_fund_employer_component", "label": "PF Employer Component", "type": "select", "required": False, "col": 4, "url_name": "salary_component_select"},
            {"name": "ssf_employee_component", "label": "SSF Employee Component", "type": "select", "required": False, "col": 4, "url_name": "salary_component_select"},
            {"name": "ssf_employer_component", "label": "SSF Employer Component", "type": "select", "required": False, "col": 4, "url_name": "salary_component_select"},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 3},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "organization", "title": "Organization"},
            {"name": "branch", "title": "Branch"},
            {"name": "default_working_days", "title": "Working Days"},
            {"name": "overtime_calculation_method", "title": "Overtime Method"},
            {"name": "rounding_method", "title": "Rounding"},
            {"name": "tax_deduction_component", "title": "Tax Component"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "updated_at", "title": "Updated At"},
        ],
        reset_defaults={"default_working_days": 30, "is_active": True},
    )
)
