from core.datatables.views import BaseDataTableView
from nepanest.common.helpers.helper import encode_date_for_display

from nepanest.modules.recruitment.models import Hire


HIRE_COLUMNS = [
    ("id", "id"),
    ("candidate", "candidate.name"),
    ("employee", lambda obj: str(obj.employee) if obj.employee else ""),
    ("hire_date", lambda obj, request: encode_date_for_display(obj.hire_date, request)),
    ("designation", lambda obj: str(obj.designation) if obj.designation else ""),
    ("department", lambda obj: str(obj.department) if obj.department else ""),
    ("status", "status"),
]


class HireDataTableView(BaseDataTableView):
    model = Hire
    columns = HIRE_COLUMNS
    searchable_columns = [
        "candidate__name",
        "candidate__email",
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "designation__name",
        "department__name",
        "status",
    ]
    orderable_columns = [
        "candidate__name",
        "employee__employee_id",
        "hire_date",
        "designation__name",
        "department__name",
        "status",
    ]
