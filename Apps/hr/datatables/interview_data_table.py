from core.datatables.views import BaseDataTableView
from ..models import Interview


INTERVIEW_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class InterviewDataTableView(BaseDataTableView):
    model = Interview
    columns = INTERVIEW_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
