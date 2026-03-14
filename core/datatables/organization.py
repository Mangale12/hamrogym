from core.datatables.views import BaseDataTableView
from core.models import Organization


class OrganizationDataTableView(BaseDataTableView):
    model = Organization
    columns = [
        ("id", "id"),
        ("name", "name"),
        ("code", "code"),
        ("is_active", "is_active"),
    ]
    searchable_columns = ["name", "code"]
    orderable_columns = ["name", "code", "is_active"]
