from core.datatables.views import BaseDataTableView
from nepanest.foundation.geography import State


class StateDataTableView(BaseDataTableView):
    model = State
    columns = [
        ("name", "name"),
        ("country", "country.name"),
        ("code", "code"),
        ("is_active", "is_active"),
        ("id", "id"),
    ]
    searchable_columns = ["name", "code", "country__name"]
    orderable_columns = ["name", "country__name", "code", "is_active", "id"]
