from core.datatables.views import BaseDataTableView
from ..models import JobSkill


JOB_SKILL_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class JobSkillDataTableView(BaseDataTableView):
    model = JobSkill
    columns = JOB_SKILL_COLUMNS
    searchable_columns = [
        "name",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "is_active",
        "remarks",
    ]
