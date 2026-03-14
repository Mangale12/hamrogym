from core.datatables.views import BaseDataTableView
from core.models import Branch


class BranchDataTableView(BaseDataTableView):
    model = Branch
    columns = [
        ("id", "id"),
        ("organization", "organization.name"),
        ("name", "name"),
        ("code", "code"),
        ("is_active", "is_active"),
    ]
    searchable_columns = ["name", "code", "organization__name"]
    orderable_columns = ["organization__name", "name", "code", "is_active"]
