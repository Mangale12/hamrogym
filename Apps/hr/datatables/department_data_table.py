from core.datatables.views import BaseDataTableView

from Apps.hr.models import Department


DEPARTMENT_COLUMNS = [
    ("id", "id"),
    ("organization", "organization.name"),
    ("branch", "branch.name"),
    ("name", "name"),
    ("code", "code"),
    ("is_active", "is_active"),
]


class DepartmentDataTableView(BaseDataTableView):
    model = Department
    columns = DEPARTMENT_COLUMNS
    searchable_columns = ["name", "code", "organization__name", "branch__name"]
    orderable_columns = ["organization__name", "branch__name", "name", "code", "is_active"]
