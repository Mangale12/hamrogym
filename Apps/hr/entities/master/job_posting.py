import re
from typing import Dict, List

from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_posting_data_table import (
    JOB_POSTING_COLUMNS,
    JobPostingDataTableView,
)
from ...forms.job_posting_form import JobPostingForm
from ...models import JobPosting, JobPostingChannelMap


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


def _parse_dynamic_section(request, section_name: str) -> List[Dict[str, object]]:
    pattern = re.compile(rf"^{re.escape(section_name)}\[(\d+)\]\[(.+)\]$")
    rows: Dict[int, Dict[str, object]] = {}

    for key, value in request.POST.items():
        match = pattern.match(key)
        if not match:
            continue
        index = int(match.group(1))
        field_name = match.group(2)
        rows.setdefault(index, {})[field_name] = value

    return [rows[idx] for idx in sorted(rows.keys())]


def _save_job_posting_channels(request, job_posting: JobPosting) -> None:
    rows = _parse_dynamic_section(request, "channels")
    existing = {
        item.id: item
        for item in JobPostingChannelMap.objects.filter(job_posting=job_posting)
    }
    keep_ids = []

    for row in rows:
        item_id = row.get("id")
        item = None

        if item_id and str(item_id).isdigit():
            item = existing.get(int(item_id))

        if not item:
            item = JobPostingChannelMap(job_posting=job_posting)

        channel_id = row.get("job_posting_channel")
        posted_url = (row.get("posted_url") or "").strip()
        posted_date = row.get("posted_date") or None

        if not any([channel_id, posted_url, posted_date]):
            continue

        if not channel_id:
            continue

        item.job_posting_channel_id = channel_id
        item.posted_url = posted_url or None
        item.posted_date = posted_date or None
        item.save()
        keep_ids.append(item.id)

    queryset = JobPostingChannelMap.objects.filter(job_posting=job_posting)
    if keep_ids:
        queryset.exclude(id__in=keep_ids).delete()
    else:
        queryset.delete()


def _load_job_posting_channels(job_posting: JobPosting) -> Dict[str, List[Dict[str, object]]]:
    return {
        "channels": [
            {
                "id": item.id,
                "job_posting_channel": str(item.job_posting_channel_id or ""),
                "posted_url": item.posted_url or "",
                "posted_date": item.posted_date.isoformat() if item.posted_date else "",
            }
            for item in JobPostingChannelMap.objects.filter(job_posting=job_posting)
            .select_related("job_posting_channel")
            .order_by("id")
        ]
    }


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
        reset_defaults={},
    )
)
