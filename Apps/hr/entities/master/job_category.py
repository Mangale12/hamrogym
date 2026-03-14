from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_category_data_table import (
    JOB_CATEGORY_COLUMNS,
    job_categoryDataTableView,
)
from ...forms.job_category_form import job_categoryForm
from ...models import job_category


register_entity(
    EntityConfig(
        name="job_category",
        url_path="job-categories",
        verbose_name="Job Categories",
        model=job_category,
        form_class=job_categoryForm,
        datatable_view=job_categoryDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_CATEGORY_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
