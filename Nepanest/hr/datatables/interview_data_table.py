from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_datetime_for_display

from ..models import Interview


INTERVIEW_COLUMNS = [
    ("id", "id"),
    ("job_application", lambda obj: str(obj.job_application)),
    ("applicant", "job_application.applicant.name"),
    ("job_posting", "job_application.job_posting.title"),
    ("interview_stage", "interview_stage.name"),
    ("sequence", "sequence"),
    ("scheduled_at", lambda obj, request: encode_datetime_for_display(obj.scheduled_at, request)),
    ("location", "location"),
    ("mode", lambda obj: obj.get_mode_display()),
    ("status", lambda obj: obj.get_status_display()),
    ("is_active", lambda obj: "Yes" if obj.is_active else "No"),
    ("remarks", "remarks"),
]


class InterviewDataTableView(BaseDataTableView):
    model = Interview
    columns = INTERVIEW_COLUMNS
    searchable_columns = [
        "job_application__applicant__name",
        "job_application__applicant__email",
        "job_application__job_posting__title",
        "interview_stage__name",
        "location",
        "mode",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "job_application__applicant__name",
        "job_application__applicant__name",
        "job_application__job_posting__title",
        "interview_stage__sequence",
        "sequence",
        "scheduled_at",
        "location",
        "mode",
        "status",
        "is_active",
        "remarks",
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("job_application__applicant", "job_application__job_posting", "interview_stage")
        )
