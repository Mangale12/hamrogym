from core.config import EntityConfig
from core.registry import register_entity

from Apps.hr.datatables.designation_data_table import (
    DESIGNATION_COLUMNS,
    DesignationDataTableView,
)
from Apps.hr.forms import DesignationForm
from Apps.hr.models import Designation


_datatable_columns = []
for key, _accessor in DESIGNATION_COLUMNS:
    if key == "id":
        continue
    column = {"name": key, "title": key.replace("_", " ").title()}
    if key == "is_active":
        column["title"] = "Active"
        column["render"] = "function(data){return data ? 'Yes' : 'No';}"
    _datatable_columns.append(column)


register_entity(
    EntityConfig(
        name="designation",
        url_path="designations",
        verbose_name="Designation",
        model=Designation,
        form_class=DesignationForm,
        datatable_view=DesignationDataTableView,
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
                "label": "Designation Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Manager",
            },
            {
                "name": "level",
                "label": "Level",
                "type": "number",
                "required": False,
                "col": 3,
                "placeholder": "1",
                "attributes": {"min": "1"},
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
