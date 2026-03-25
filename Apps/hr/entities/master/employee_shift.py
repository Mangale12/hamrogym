from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.employee_shift_data_table import EmployeeShiftDataTableView, EMPLOYEE_SHIFT_COLUMNS
from ...forms.employee_shift_form import EmployeeShiftForm
from ...models import EmployeeShift


register_entity(
    EntityConfig(
        name="employee_shift",
        url_path="employee-shifts",
        verbose_name="Employee Shift",
        model=EmployeeShift,
        form_class=EmployeeShiftForm,
        datatable_view=EmployeeShiftDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in EMPLOYEE_SHIFT_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
