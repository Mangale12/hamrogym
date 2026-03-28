from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import PayrollRunComponentDataTableView
from ...forms.payroll_form import PayrollRunComponentForm
from ...models import PayrollRunComponent
from .payroll_shared import payroll_run_component_columns


register_entity(
    EntityConfig(
        name="payroll_run_component",
        url_path="payroll-run-components",
        verbose_name="Payroll Run Component",
        model=PayrollRunComponent,
        form_class=PayrollRunComponentForm,
        datatable_view=PayrollRunComponentDataTableView,
        fields=[
            {"name": "payroll_run_employee", "label": "Payroll Employee", "type": "select", "required": True, "col": 6, "url_name": "payroll_run_employee_select"},
            {"name": "salary_component", "label": "Salary Component", "type": "select", "required": True, "col": 6, "url_name": "salary_component_select"},
            {"name": "source_type", "label": "Source Type", "type": "static_select", "required": True, "col": 3, "options": PayrollRunComponent._meta.get_field("source_type").choices},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": True, "col": 3},
            {"name": "quantity", "label": "Quantity", "type": "number", "required": False, "col": 3},
            {"name": "rate", "label": "Rate", "type": "number", "required": False, "col": 3},
            {"name": "amount", "label": "Amount", "type": "number", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=payroll_run_component_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "payroll_run_employee__payroll_run__name",
            "payroll_run_employee__employee__employee_id",
            "salary_component__code",
            "salary_component__name",
        ],
    )
)
