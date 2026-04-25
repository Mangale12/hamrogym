from core.config import EntityConfig
from core.registry import register_entity
from nepanest.modules.recruitment.datatables import (
    JOB_CATEGORY_COLUMNS,
    JobCategoryDataTableView,
)
from nepanest.modules.recruitment.forms import JobCategoryForm
from nepanest.modules.recruitment.models import JobCategory


register_entity(
    EntityConfig(
        name="job_category",
        url_path="job-categories",
        verbose_name="Job Categories",
        model=JobCategory,
        form_class=JobCategoryForm,
        datatable_view=JobCategoryDataTableView,
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
