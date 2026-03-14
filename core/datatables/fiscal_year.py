from core.datatables.views import BaseDataTableView
from core.models import FiscalYear


class FiscalYearDataTableView(BaseDataTableView):
    model = FiscalYear
    columns = [
        ("name", "name"),
        ("start_date", lambda o: o.start_date.strftime("%Y-%m-%d")),
        ("end_date", lambda o: o.end_date.strftime("%Y-%m-%d")),
        ("is_active", "is_active"),
        ("is_closed", "is_closed"),
        ("id", "id"),
    ]
    searchable_columns = ["name"]
    orderable_columns = ["name", "start_date", "end_date", "is_active", "is_closed", "id"]
