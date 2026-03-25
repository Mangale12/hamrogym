from core.datatables.views import BaseDataTableView
from ..models import Policy


POLICY_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class PolicyDataTableView(BaseDataTableView):
    model = Policy
    columns = POLICY_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
