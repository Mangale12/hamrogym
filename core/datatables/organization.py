from core.datatables.views import BaseDataTableView
from nepanest.foundation.organization import Organization


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
