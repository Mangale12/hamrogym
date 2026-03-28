from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import TaxSlabDataTableView
from ...forms.payroll_form import TaxSlabForm
from ...models import TaxSlab


register_entity(
    EntityConfig(
        name="tax_slab",
        url_path="tax-slabs",
        verbose_name="Tax Slab",
        model=TaxSlab,
        form_class=TaxSlabForm,
        datatable_view=TaxSlabDataTableView,
        fields=[
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": True, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "min_income", "label": "Min Income", "type": "number", "required": True, "col": 2, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "max_income", "label": "Max Income", "type": "number", "required": False, "col": 2, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "tax_rate", "label": "Tax Rate %", "type": "number", "required": True, "col": 2, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "rebate_amount", "label": "Rebate Amount", "type": "number", "required": False, "col": 2, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 3},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "fiscal_year", "title": "Fiscal Year"},
            {"name": "min_income", "title": "Min Income"},
            {"name": "max_income", "title": "Max Income"},
            {"name": "tax_rate", "title": "Tax Rate"},
            {"name": "rebate_amount", "title": "Rebate"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
        ],
        reset_defaults={"is_active": True},
    )
)
