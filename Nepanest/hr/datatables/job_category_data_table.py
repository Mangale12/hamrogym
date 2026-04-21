from core.datatables.views import BaseDataTableView
from ..models import JobCategory


JOB_CATEGORY_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class JobCategoryDataTableView(BaseDataTableView):
    model = JobCategory
    columns = JOB_CATEGORY_COLUMNS
    searchable_columns = [
        "name",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "is_active",
    ]
