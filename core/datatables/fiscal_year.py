from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display
from core.models import FiscalYear


class FiscalYearDataTableView(BaseDataTableView):
    model = FiscalYear
    columns = [
        ("name", "name"),
        ("start_date", lambda obj, request: encode_date_for_display(obj.start_date, request)),
        ("end_date", lambda obj, request: encode_date_for_display(obj.end_date, request)),
        ("is_active", "is_active"),
        ("is_current", "is_current"),
        ("is_closed", "is_closed"),
        ("id", "id"),
    ]
    searchable_columns = ["name"]
    orderable_columns = ["name", "start_date", "end_date", "is_active", "is_current", "is_closed", "id"]
