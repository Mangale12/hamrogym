from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.brand_data_table import BrandDataTableView, BRAND_COLUMNS
from ...forms.brand_form import BrandForm
from ...models import Brand


register_entity(
    EntityConfig(
        name="brand",
        url_path="brands",
        verbose_name="Brands",
        model=Brand,
        form_class=BrandForm,
        datatable_view=BrandDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": True,
                "col": 6,
            },
            {
                "name": "is_active",
                "label": "Is Active",
                "type": "checkbox",
                "required": False,
                "col": 12,
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
            for key, _accessor in BRAND_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
