from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_position_data_table import (
    JOB_POSITION_COLUMNS,
    JobPositionDataTableView,
)
from ...forms.job_position_form import JobPositionForm
from ...models import JobPosition


register_entity(
    EntityConfig(
        name="job_position",
        url_path="job_position",
        verbose_name="Job Position",
        model=JobPosition,
        form_class=JobPositionForm,
        datatable_view=JobPositionDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "department", "label": "Department", "type": "select",  "required": True, "col": 6, "url_name": "department_select"},
            {"name": "designation", "label": "Designation", "type": "select",  "required": True, "col": 6, "url_name": "designation_select"},
            {"name": "job_category", "label": "Job Category", "type": "select",  "required": True, "col": 6, "url_name": "job_category_select"},
            {"name": "vacancies", "label": "Vacancies", "type": "number", "required": True, "col": 6},
            {"name": "employeement_type", "label": "Employment Type", "type": "select", "required": False, "col": 12, "url_name": "employeement_type_select"},
            {"name": "salary_min", "label": "Salary Min", "type": "number", "required": False, "col": 12},
            {"name": "salary_max", "label": "Salary Max", "type": "number", "required": False, "col": 12},
            {"name": "is_active", "label": "Is Active", "type": "boolean", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_POSITION_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
