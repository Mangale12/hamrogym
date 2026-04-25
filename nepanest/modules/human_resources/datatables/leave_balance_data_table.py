from core.datatables.views import BaseDataTableView
from nepanest.common.helpers.helper import encode_date_for_display, encode_datetime_for_display

from nepanest.modules.leave.models import LeaveAccrual, LeaveBalance, LeaveLedger


LEAVE_BALANCE_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("leave_type", lambda obj: str(obj.leave_type)),
    ("year", "year"),
    ("opening_balance", "opening_balance"),
    ("accrued", "accrued"),
    ("used", "used"),
    ("encashed", "encashed"),
    ("balance", "balance"),
    ("updated_at", lambda obj, request: encode_datetime_for_display(obj.updated_at, request)),
]


LEAVE_LEDGER_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("leave_type", lambda obj: str(obj.leave_type)),
    ("year", "year"),
    ("change_type", "change_type"),
    ("days", "days"),
    ("reference_type", "reference_type"),
    ("reference_id", "reference_id"),
    ("balance_after", "balance_after"),
    ("created_at", lambda obj, request: encode_datetime_for_display(obj.created_at, request)),
]


LEAVE_ACCRUAL_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("leave_type", lambda obj: str(obj.leave_type)),
    ("policy", lambda obj: str(obj.policy) if obj.policy else ""),
    ("accrual_date", lambda obj, request: encode_date_for_display(obj.accrual_date, request)),
    ("days_added", "days_added"),
    ("created_at", lambda obj, request: encode_datetime_for_display(obj.created_at, request)),
]


class LeaveBalanceDataTableView(BaseDataTableView):
    model = LeaveBalance
    columns = LEAVE_BALANCE_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "leave_type__name",
        "year",
    ]
    orderable_columns = [
        "employee__employee_id",
        "leave_type__name",
        "year",
        "balance",
        "updated_at",
    ]


class LeaveLedgerDataTableView(BaseDataTableView):
    model = LeaveLedger
    columns = LEAVE_LEDGER_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "leave_type__name",
        "change_type",
        "reference_type",
        "remarks",
    ]
    orderable_columns = [
        "employee__employee_id",
        "leave_type__name",
        "year",
        "change_type",
        "created_at",
    ]


class LeaveAccrualDataTableView(BaseDataTableView):
    model = LeaveAccrual
    columns = LEAVE_ACCRUAL_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "leave_type__name",
        "policy__leave_type__name",
        "remarks",
    ]
    orderable_columns = [
        "employee__employee_id",
        "leave_type__name",
        "accrual_date",
        "days_added",
        "created_at",
    ]
