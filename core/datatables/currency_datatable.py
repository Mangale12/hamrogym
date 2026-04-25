from core.datatables.views import BaseDataTableView
from nepanest.foundation.fiscal import Currency


class CurrencyDataTableView(BaseDataTableView):
    model = Currency
    columns = [
        ("code", "code"),
        ("name", "name"),
        ("symbol", "symbol"),
        ("id", "id"),
    ]
    searchable_columns = ["code", "name", "symbol"]
    orderable_columns = ["code", "name", "symbol", "id"]
