from core.config import EntityConfig
from core.registry import register_entity

from Apps.hr.datatables.department_data_table import (
    DEPARTMENT_COLUMNS,
    DepartmentDataTableView,
)
from Apps.hr.forms import DepartmentForm
from Apps.hr.models import Department


_datatable_columns = []
for key, _accessor in DEPARTMENT_COLUMNS:
    if key == "id":
        continue
    column = {"name": key, "title": key.replace("_", " ").title()}
    if key == "is_active":
        column["title"] = "Active"
        column["render"] = "function(data){return data ? 'Yes' : 'No';}"
    _datatable_columns.append(column)


register_entity(
    EntityConfig(
        name="department",
        url_path="departments",
        verbose_name="Department",
        model=Department,
        form_class=DepartmentForm,
        datatable_view=DepartmentDataTableView,
        fields=[
            {
                "name": "organization",
                "label": "Organization",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "organization_select",
            },
            {
                "name": "branch",
                "label": "Branch",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "branch_select",
            },
            {
                "name": "name",
                "label": "Department Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Human Resources",
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": False,
                "col": 3,
                "placeholder": "HR",
            },
            {
                "name": "is_active",
                "label": "Active",
                "type": "checkbox",
                "required": False,
                "col": 3,
                "default": True,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
                "placeholder": "Optional notes",
            },
        ],
        datatable_columns=_datatable_columns,
        reset_defaults={"is_active": True},
    )
)
