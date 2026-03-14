from core.datatables.views import BaseDataTableView
from ..models import JobPosting


JOB_POSTING_COLUMNS = [
    ("id", "id"),
    ("job_position", "job_position.name"),
    ("posting_date", "posting_date"),
    ("closing_date", "closing_date"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class job_postingDataTableView(BaseDataTableView):
    model = JobPosting
    columns = JOB_POSTING_COLUMNS
    searchable_columns = [
       "job_position__name",
       "posting_date",
       "closing_date",
       "is_active",
       "remarks",
    ]
    orderable_columns = [
        "job_position__name",
        "posting_date",
        "closing_date",
        "is_active",
        "remarks",
    ]
