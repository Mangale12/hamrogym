from core.datatables.views import BaseDataTableView
from nepanest.common.helpers.helper import encode_datetime_for_display
from nepanest.modules.recruitment.models import JobApplication


JOB_APPLICATION_COLUMNS = [
    ("id", "id"),
    ("applicant", "applicant.name"),
    ("job_posting", "job_posting.title"),
    ("status", "status"),
    ("applied_date", lambda obj, request: encode_datetime_for_display(obj.applied_date, request)),
    ("is_active", lambda obj: "Yes" if obj.is_active else "No"),
    ("remarks", "remarks"),
]


class JobApplicationDataTableView(BaseDataTableView):
    model = JobApplication
    columns = JOB_APPLICATION_COLUMNS
    searchable_columns = [
        "applicant__name",
        "applicant__email",
        "job_posting__title",
        "job_posting__job_position__name",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "applicant__name",
        "job_posting__title",
        "status",
        "applied_date",
        "is_active",
        "remarks",
    ]
