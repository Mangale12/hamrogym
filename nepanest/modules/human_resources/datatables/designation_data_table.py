from core.datatables.views import BaseDataTableView

from nepanest.modules.people.models import Designation


DESIGNATION_COLUMNS = [
    ("id", "id"),
    ("organization", "organization.name"),
    ("branch", "branch.name"),
    ("name", "name"),
    ("level", "level"),
    ("is_active", "is_active"),
]


class DesignationDataTableView(BaseDataTableView):
    model = Designation
    columns = DESIGNATION_COLUMNS
    searchable_columns = ["name", "organization__name", "branch__name"]
    orderable_columns = ["organization__name", "branch__name", "name", "level", "is_active"]
