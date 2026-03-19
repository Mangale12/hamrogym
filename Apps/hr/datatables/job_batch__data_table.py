from core.datatables.views import BaseDataTableView
from ..models import JobBatches


JOB_BATCH__COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("hiring_plan", "hiring_plan.name"),
    ("code", "code"),
    ("branch", "branch.name"),
    ("status", "status"),
    ("approved_by", "approved_by.username"),
    ("approved_at", "approved_at"),
    ("start_date", "start_date"),
    ("end_date", "end_date"),
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
