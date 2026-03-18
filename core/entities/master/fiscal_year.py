from core.config import EntityConfig
from core.datatables.fiscal_year import FiscalYearDataTableView
from core.forms import FiscalYearForm
from core.models import FiscalYear
from core.registry import register_entity


register_entity(
    EntityConfig(
        name="fiscal_year",
        url_path="fiscal-years",
        verbose_name="Fiscal Year",
        model=FiscalYear,
        form_class=FiscalYearForm,
        datatable_view=FiscalYearDataTableView,
        fields=[
            {
                "name": "name",
                "label": "Fiscal Year Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "FY 2081/82",
            },
            {
                "name": "start_date",
                "label": "Start Date",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {
                "name": "end_date",
                "label": "End Date",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {
                "name": "is_active",
                "label": "Active",
                "type": "checkbox",
                "required": False,
                "col": 6,
                "default": True,
            },
            {
                "name": "is_current",
                "label": "Current",
                "type": "checkbox",
                "required": False,
                "col": 6,
                "default": False,
            },
            {
                "name": "is_closed",
                "label": "Closed",
                "type": "checkbox",
                "required": False,
                "col": 6,
                "default": False,
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
        datatable_columns=[
            {"name": "name", "title": "Name"},
            {"name": "start_date", "title": "Start Date"},
            {"name": "end_date", "title": "End Date"},
            {
                "name": "is_active",
                "title": "Active",
                "render": "function(data){return data ? 'Yes' : 'No';}",
            },
            {
                "name": "is_current",
                "title": "Current",
                "render": "function(data){return data ? 'Yes' : 'No';}",
            },
            {
                "name": "is_closed",
                "title": "Closed",
                "render": "function(data){return data ? 'Yes' : 'No';}",
            },
        ],
        reset_defaults={"is_active": True, "is_current": False, "is_closed": False},
    )
)
