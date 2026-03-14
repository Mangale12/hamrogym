from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_posting_data_table import (
    JOB_POSTING_COLUMNS,
    job_postingDataTableView,
)
from ...forms.job_posting_form import job_postingForm
from ...models import JobPosting


register_entity(
    EntityConfig(
        name="job_posting",
        url_path="job-postings",
        verbose_name="Job Posting",
        model=JobPosting,
        form_class=job_postingForm,
        datatable_view=job_postingDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "job_position", "label": "Job Position", "type": "select", "required": True, "col": 6, "url_name": "job_position_select"},
            {"name": "posting_date", "label": "Posting Date", "type": "date", "required": True, "col": 6},
            {"name": "closing_date", "label": "Closing Date", "type": "date", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "boolean", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_POSTING_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
