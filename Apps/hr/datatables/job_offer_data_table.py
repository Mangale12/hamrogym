from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display

from ..models import JobOffer


JOB_OFFER_COLUMNS = [
    ("id", "id"),
    ("job_application", lambda obj: str(obj.job_application)),
    ("offer_date", lambda obj, request: encode_date_for_display(obj.offer_date, request)),
    ("joining_date", lambda obj, request: encode_date_for_display(obj.joining_date, request)),
    ("salary_offered", lambda obj: str(obj.salary_offered)),
    ("status", "status"),
    ("attachments", lambda obj: obj.attachments.count()),
    ("remarks", "remarks"),
]


class JobOfferDataTableView(BaseDataTableView):
    model = JobOffer
    columns = JOB_OFFER_COLUMNS
    searchable_columns = [
        "job_application__applicant__name",
        "job_application__applicant__email",
        "job_application__job_posting__title",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "job_application__applicant__name",
        "offer_date",
        "joining_date",
        "salary_offered",
        "status",
        "remarks",
    ]
