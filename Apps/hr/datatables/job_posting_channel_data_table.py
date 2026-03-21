from core.datatables.views import BaseDataTableView
from ..models import JobPostingChannel


JOB_POSTING_CHANNEL_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class JobPostingChannelDataTableView(BaseDataTableView):
    model = JobPostingChannel
    columns = JOB_POSTING_CHANNEL_COLUMNS
    searchable_columns = [
        "name",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "is_active",
        "remarks",
    ]
