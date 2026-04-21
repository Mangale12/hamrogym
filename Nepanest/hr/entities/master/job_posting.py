from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_posting_data_table import (
    JOB_POSTING_COLUMNS,
    JobPostingDataTableView,
)
from ...forms.job_posting_form import JobPostingForm
from ...models import JobPosting, JobPostingChannelMap
from core.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)
from datetime import datetime

CHANNEL_MAP_SECTION = {
    "title": "Posting Channels",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "job_posting_channel",
            "label": "Channel",
            "type": "select",
            "required": True,
            "url_name": "job_posting_channel_select",
        },
        {
            "name": "posted_url",
            "label": "Posted URL",
            "type": "text",
            "required": False,
        },
        {
            "name": "posted_date",
            "label": "Posted Date",
            "type": "date",
            "required": False,
        },
    ],
}


CHANNEL_MAP_SECTION_RELATION = RelatedDynamicSectionConfig(
    section_name="channels",
    related_model=JobPostingChannelMap,
    parent_field="job_posting",
    fields=["job_posting_channel", "posted_url", "posted_date"],
    required_fields=["job_posting_channel"],
    bool_fields=[],
    empty_check_fields=["job_posting_channel", "posted_url", "posted_date"],
    save_transformers={
        "job_posting_channel": lambda value: (value or "").strip(),
        "posted_url": lambda value: (value or "").strip(),
        "posted_date": lambda value: (value or datetime.now()),
    },
)

_save_job_posting_channels = build_related_section_saver(CHANNEL_MAP_SECTION_RELATION)
_load_job_posting_channels = build_related_section_loader(CHANNEL_MAP_SECTION_RELATION)

register_entity(
    EntityConfig(
        name="job_posting",
        url_path="job-postings",
        verbose_name="Job Posting",
        model=JobPosting,
        form_class=JobPostingForm,
        datatable_view=JobPostingDataTableView,
        fields=[
            {"name": "title", "label": "Title", "type": "text", "required": True, "col": 6},
            {"name": "job_position", "label": "Job Position", "type": "select", "required": True, "col": 6, "url_name": "job_position_select"},
            {"name": "posting_date", "label": "Posting Date", "type": "date", "required": True, "col": 6},
            {"name": "closing_date", "label": "Closing Date", "type": "date", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        dynamic_sections={
            "channels": CHANNEL_MAP_SECTION,
        },
        dynamic_sections_loader=_load_job_posting_channels,
        dynamic_sections_saver=_save_job_posting_channels,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_POSTING_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
    )
)
