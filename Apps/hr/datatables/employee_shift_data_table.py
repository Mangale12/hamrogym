from core.datatables.views import BaseDataTableView
from ..models import EmployeeShift


EMPLOYEE_SHIFT_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class EmployeeShiftDataTableView(BaseDataTableView):
    model = EmployeeShift
    columns = EMPLOYEE_SHIFT_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
