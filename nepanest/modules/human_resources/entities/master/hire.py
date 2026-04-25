from core.choices import APPROVAL_STATUS_CHOICES
from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.recruitment.datatables import HIRE_COLUMNS, HireDataTableView
from nepanest.modules.recruitment.forms import HireForm
from nepanest.modules.recruitment.models import Hire


register_entity(
    EntityConfig(
        name="hire",
        url_path="hires",
        verbose_name="Hire",
        model=Hire,
        form_class=HireForm,
        datatable_view=HireDataTableView,
        fields=[
            {
                "name": "candidate",
                "label": "Candidate",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "applicant_select",
            },
            {
                "name": "employee",
                "label": "Employee",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "employee_select",
            },
            {
                "name": "hire_date",
                "label": "Hire Date",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {
                "name": "designation",
                "label": "Designation",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "designation_select",
            },
            {
                "name": "department",
                "label": "Department",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "department_select",
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": APPROVAL_STATUS_CHOICES,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in HIRE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": "pending"},
        select_search_fields=[
            "candidate__name",
            "candidate__email",
            "employee__employee_id",
            "designation__name",
            "department__name",
            "status",
        ],
    )
)
