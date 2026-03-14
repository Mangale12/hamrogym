from core.datatables.views import BaseDataTableView

from Apps.hr.models import Employee


def _safe_related(obj, attr, field):
    try:
        related = getattr(obj, attr)
    except Exception:
        return ""
    return getattr(related, field, "") or ""


EMPLOYEE_COLUMNS = [
    ("id", "id"),
    ("employee_id", "employee_id"),
    ("user", lambda obj: obj.user.get_full_name() or obj.user.username),
    ("username", "user.username"),
    ("email", "user.email"),
    ("organization", "organization.name"),
    ("branch", "branch.name"),
    ("department", "department.name"),
    ("designation", "designation.name"),
    ("employment_status", lambda obj: obj.get_employment_status_display() if obj.employment_status else ""),
    ("phone", lambda obj: _safe_related(obj, "contact", "phone")),
    ("join_date", lambda obj: obj.join_date.strftime("%Y-%m-%d") if obj.join_date else ""),
    ("is_active", "is_active"),
]


class EmployeeDataTableView(BaseDataTableView):
    model = Employee
    columns = EMPLOYEE_COLUMNS
    searchable_columns = [
        "employee_id",
        "employee_code",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "organization__name",
        "branch__name",
        "department__name",
        "designation__name",
        "employment_status",
        "contact__phone",
    ]
    orderable_columns = [
        "employee_id",
        "user__first_name",
        "user__username",
        "user__email",
        "organization__name",
        "branch__name",
        "department__name",
        "designation__name",
        "employment_status",
        "join_date",
        "is_active",
    ]
