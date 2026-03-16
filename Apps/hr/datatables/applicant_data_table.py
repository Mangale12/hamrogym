from core.datatables.views import BaseDataTableView
from ..models import Applicant


APPLICANT_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("email", "email"),
    ("phone", "phone"),
    ("gender", "gender"),
    ("marital_status", "marital_status"),
    ("status", "status"),
    ("date", "date"),
    ("country", "country.name"),
    ("state", "state.name"),
    ("city", "city"),
    ("cv", lambda obj: obj.cv.url if obj.cv else ""),
    ("cover_letter", lambda obj: obj.cover_letter.url if obj.cover_letter else ""),
]


class ApplicantDataTableView(BaseDataTableView):
    model = Applicant
    columns = APPLICANT_COLUMNS
    searchable_columns = [
        "name",
        "email",
        "phone",
        "gender",
        "marital_status",
        "status",
        "date",
        "country__name",
        "state__name",
        "job_posting__job_position__name",
        "city",
        "cv",
        "cover_letter",
    ]
    orderable_columns = [
        "name",
        "email",
        "phone",
        "gender",
        "marital_status",
        "status",
        "date",
        "country__name",
        "state__name",
        "city",
        "cv",
        "cover_letter",
    ]
