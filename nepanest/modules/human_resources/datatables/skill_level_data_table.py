from core.datatables.views import BaseDataTableView
from nepanest.modules.recruitment.models import SkillLevel


SKILL_LEVEL_COLUMNS = [
    ("id", "id"),
        ("name", "name"),
        ("is_active", "is_active"),
        ("remarks", "remarks"),
    # TODO: add columns
]


class SkillLevelDataTableView(BaseDataTableView):
    model = SkillLevel
    columns = SKILL_LEVEL_COLUMNS
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
