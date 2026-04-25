from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.payroll.datatables import ProvidentFundDataTableView
from nepanest.modules.payroll.forms import ProvidentFundForm
from nepanest.modules.payroll.models import ProvidentFund


register_entity(
    EntityConfig(
        name="provident_fund",
        url_path="provident-funds",
        verbose_name="Provident Fund",
        model=ProvidentFund,
        form_class=ProvidentFundForm,
        datatable_view=ProvidentFundDataTableView,
        fields=[
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 4, "url_name": "employee_select"},
            {"name": "employee_percent", "label": "Employee %", "type": "number", "required": True, "col": 2, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "employer_percent", "label": "Employer %", "type": "number", "required": True, "col": 2, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "effective_from", "label": "Effective From", "type": "date", "required": True, "col": 2},
            {"name": "effective_to", "label": "Effective To", "type": "date", "required": False, "col": 2},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 3},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "employee", "title": "Employee"},
            {"name": "employee_percent", "title": "Employee %"},
            {"name": "employer_percent", "title": "Employer %"},
            {"name": "effective_from", "title": "Effective From"},
            {"name": "effective_to", "title": "Effective To"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
        ],
        reset_defaults={"effective_from": timezone.localdate().isoformat(), "is_active": True},
    )
)
