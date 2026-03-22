from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display
from ..models import JobPosting


JOB_POSTING_COLUMNS = [
    ("id", "id"),
    ("title", "title"),
    ("job_position", "job_position__name"),
    ("posting_date", lambda obj, request: encode_date_for_display(obj.posting_date, request)),
    ("closing_date", lambda obj, request: encode_date_for_display(obj.closing_date, request)),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class JobPostingDataTableView(BaseDataTableView):
    model = JobPosting
    columns = JOB_POSTING_COLUMNS
    searchable_columns = [
       "title",
       "job_position__name",
       "posting_date",
       "closing_date",
       "is_active",
       "remarks",
    ]
    orderable_columns = [
        "title",
        "job_position__name",
        "posting_date",
        "closing_date",
        "is_active",
        "remarks",
    ]
