from core.datatables.views import BaseDataTableView
from ..models import LeadStatus


LEAD_STATUS_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("sequence", "sequence"),
    ("is_default", "is_default"),
    ("is_active", "is_active"),
    ("color", "color"),
    ("is_closed", "is_closed"),
    ("remarks", "remarks"),
]


class LeadStatusDataTableView(BaseDataTableView):
    model = LeadStatus
    columns = LEAD_STATUS_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "code",
        "sequence",
        "is_default",
        "is_active",
        "color",
        "is_closed",
        "remarks",
    ]
