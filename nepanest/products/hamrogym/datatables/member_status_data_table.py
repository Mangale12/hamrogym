from core.datatables.views import BaseDataTableView

from ..models import MemberStatus


MEMBER_STATUS_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class MemberStatusDataTableView(BaseDataTableView):
    model = MemberStatus
    columns = MEMBER_STATUS_COLUMNS
    searchable_columns = ["name", "code", "remarks"]
    orderable_columns = ["name", "code", "is_active", "remarks"]

    def serialize_row(self, obj):
        row = super().serialize_row(obj)
        row["is_system"] = obj.is_system
        return row
