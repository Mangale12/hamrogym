from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display
from ..models import JobBatches


JOB_BATCH__COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("hiring_plan", "hiring_plan.name"),
    ("code", "code"),
    ("branch", "branch.name"),
    ("status", "status"),
    ("approved_by", "approved_by.username"),
    (
        "approved_at",
        lambda obj, request: (
            f"{encode_date_for_display(obj.approved_at.date(), request)} {obj.approved_at.strftime('%H:%M')}"
        )
        if obj.approved_at
        else "",
    ),
    ("start_date", lambda obj, request: encode_date_for_display(obj.start_date, request)),
    ("end_date", lambda obj, request: encode_date_for_display(obj.end_date, request)),
    ("remarks", "remarks"),
]


class JobBatchesDataTableView(BaseDataTableView):
    model = JobBatches
    columns = JOB_BATCH__COLUMNS

    searchable_columns = [
        "name",
        "hiring_plan__name",
        "code",
        "branch__name",
        "status",
        "approved_by__username",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "hiring_plan__name",
        "code",
        "branch__name",
        "status",
        "approved_by__username",
        "approved_at",
        "remarks",
    ]
