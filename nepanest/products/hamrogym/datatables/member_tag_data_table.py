from core.datatables.views import BaseDataTableView
from ..models import MemberTag


MEMBER_TAG_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class MemberTagDataTableView(BaseDataTableView):
    model = MemberTag
    columns = MEMBER_TAG_COLUMNS
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
