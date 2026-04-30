from core.datatables.views import BaseDataTableView
from ..models import MembershipExtension


MEMBERSHIP_EXTENSION_COLUMNS = [
    ("id", "id"),
    ("membership", "membership"),
    ("start_date", "start_date"),
    ("end_date", "end_date"),
    ("total_days", "total_days"),
    ("reason", "reason"),
    ("approved_by", "approved_by"),
]


class MembershipExtensionDataTableView(BaseDataTableView):
    model = MembershipExtension
    columns = MEMBERSHIP_EXTENSION_COLUMNS
    searchable_columns = [
        "membership",
        "start_date",
        "end_date",
        "total_days",
        "reason",
        "approved_by",
    ]
    orderable_columns = [
        "membership",
        "start_date",
        "end_date",
        "total_days",
        "reason",
        "approved_by",
    ]
