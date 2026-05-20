from core.datatables.views import BaseDataTableView
from ..models import LeadStatus


LEAD_STATUS_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class LeadStatusDataTableView(BaseDataTableView):
    model = LeadStatus
    columns = LEAD_STATUS_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
