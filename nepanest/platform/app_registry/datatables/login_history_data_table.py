from core.datatables.views import BaseDataTableView
from ..models import LoginHistory


LOGIN_HISTORY_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class LoginHistoryDataTableView(BaseDataTableView):
    model = LoginHistory
    columns = LOGIN_HISTORY_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
