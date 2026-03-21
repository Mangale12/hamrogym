from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_posting_channel_data_table import JobPostingChannelDataTableView, JOB_POSTING_CHANNEL_COLUMNS
from ...forms.job_posting_channel_form import JobPostingChannelForm
from ...models import JobPostingChannel


register_entity(
    EntityConfig(
        name="job_posting_channel",
        url_path="job-posting-channel",
        verbose_name="Job Posting Channel",
        model=JobPostingChannel,
        form_class=JobPostingChannelForm,
        datatable_view=JobPostingChannelDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_POSTING_CHANNEL_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
