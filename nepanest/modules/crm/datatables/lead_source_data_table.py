from core.datatables.views import BaseDataTableView
from ..models import LeadSource


LEAD_SOURCE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class LeadSourceDataTableView(BaseDataTableView):
    model = LeadSource
    columns = LEAD_SOURCE_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "is_default",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
