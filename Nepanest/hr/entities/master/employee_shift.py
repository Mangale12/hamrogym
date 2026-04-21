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
            {
                "name": "employee",
                "label": "Employee",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "employee_select",
            },
            {
                "name": "shift",
                "label": "Shift",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "shift_select",
            },
            {
                "name": "effective_from",
                "label": "Effective From",
                "type": "datetime",
                "required": False,
                "col": 6,
            },
            {
                "name": "effective_to",
                "label": "Effective To",
                "type": "datetime",
                "required": False,
                "col": 6,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in EMPLOYEE_SHIFT_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
        select_search_fields=[
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "shift__name",
            "shift__code",
        ],
    )
)
