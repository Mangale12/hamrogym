from core.datatables.views import BaseDataTableView
from ..models import InterviewStage


INTERVIEW_STAGE_COLUMNS = [
    ("id", "id"),
        ("name", "name"),
        ("sequence", "sequence"),
        ("is_active", "is_active"),
        ("remarks", "remarks"),
    # TODO: add columns
]


class InterviewStageDataTableView(BaseDataTableView):
    model = InterviewStage
    columns = INTERVIEW_STAGE_COLUMNS
    searchable_columns = [
        "name",
        "sequence",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "sequence",
        "is_active",
        "remarks",
    ]
