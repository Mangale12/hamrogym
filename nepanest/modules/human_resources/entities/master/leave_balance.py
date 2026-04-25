from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.leave.datatables import (
    LEAVE_ACCRUAL_COLUMNS,
    LEAVE_BALANCE_COLUMNS,
    LEAVE_LEDGER_COLUMNS,
    LeaveAccrualDataTableView,
    LeaveBalanceDataTableView,
    LeaveLedgerDataTableView,
)
from nepanest.modules.leave.forms import LeaveAccrualForm, LeaveBalanceForm, LeaveLedgerForm
from nepanest.modules.leave.models import LeaveAccrual, LeaveBalance, LeaveLedger

_balance_columns = [
    {"name": "employee", "title": "Employee"},
    {"name": "leave_type", "title": "Leave Type"},
    {"name": "year", "title": "Year"},
    {"name": "opening_balance", "title": "Opening"},
    {"name": "accrued", "title": "Accrued"},
    {"name": "used", "title": "Used"},
    {"name": "encashed", "title": "Encashed"},
    {
        "name": "balance",
        "title": "Available",
        "render": (
            "function(data){"
            "const value=parseFloat(data||0);"
            "const cls=value < 0 ? 'danger' : (value === 0 ? 'secondary' : 'success');"
            "return `<span class=\"badge bg-${cls}\">${data}</span>`;"
            "}"
        ),
    },
    {"name": "updated_at", "title": "Last Updated"},
]

_ledger_columns = [
    {"name": "employee", "title": "Employee"},
    {"name": "leave_type", "title": "Leave Type"},
    {"name": "year", "title": "Year"},
    {
        "name": "change_type",
        "title": "Change Type",
        "render": "function(data){return (data||'').replaceAll('_',' ');}",
    },
    {"name": "days", "title": "Days"},
    {"name": "reference_type", "title": "Reference Type"},
    {"name": "reference_id", "title": "Reference ID"},
    {"name": "balance_after", "title": "Balance After"},
    {"name": "created_at", "title": "Recorded At"},
]

_accrual_columns = [
    {"name": "employee", "title": "Employee"},
    {"name": "leave_type", "title": "Leave Type"},
    {"name": "policy", "title": "Policy"},
    {"name": "accrual_date", "title": "Accrual Date"},
    {"name": "days_added", "title": "Days Added"},
    {"name": "created_at", "title": "Recorded At"},
]


register_entity(
    EntityConfig(
        name="leave_balance",
        url_path="leave-balances",
        verbose_name="Leave Balance",
        model=LeaveBalance,
        form_class=LeaveBalanceForm,
        datatable_view=LeaveBalanceDataTableView,
        fields=[
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "leave_type", "label": "Leave Type", "type": "select", "required": True, "col": 6, "url_name": "leave_type_select"},
            {"name": "year", "label": "Leave Year", "type": "number", "required": True, "col": 3},
            {"name": "opening_balance", "label": "Opening Balance", "type": "number", "required": True, "col": 3},
            {"name": "accrued", "label": "Accrued Days", "type": "number", "required": True, "col": 3},
            {"name": "used", "label": "Used Days", "type": "number", "required": True, "col": 3},
            {"name": "encashed", "label": "Encashed Days", "type": "number", "required": True, "col": 6},
            {"name": "balance", "label": "Available Balance", "type": "number", "required": True, "col": 6},
        ],
        datatable_columns=_balance_columns,
        reset_defaults={"year": timezone.localdate().year},
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "leave_type__name",
        ],
    )
)


register_entity(
    EntityConfig(
        name="leave_ledger",
        url_path="leave-ledger",
        verbose_name="Leave Ledger",
        model=LeaveLedger,
        form_class=LeaveLedgerForm,
        datatable_view=LeaveLedgerDataTableView,
        fields=[
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "leave_type", "label": "Leave Type", "type": "select", "required": True, "col": 6, "url_name": "leave_type_select"},
            {"name": "year", "label": "Ledger Year", "type": "number", "required": True, "col": 3},
            {"name": "change_type", "label": "Change Type", "type": "static_select", "required": True, "col": 3, "options": LeaveLedger._meta.get_field("change_type").choices},
            {"name": "days", "label": "Days Changed", "type": "number", "required": True, "col": 3},
            {"name": "balance_after", "label": "Balance After Entry", "type": "number", "required": False, "col": 3},
            {"name": "reference_type", "label": "Reference Type", "type": "text", "required": False, "col": 6, "placeholder": "LeaveRequest / LeaveAccrual / Adjustment"},
            {"name": "reference_id", "label": "Reference ID", "type": "number", "required": False, "col": 6},
            {"name": "remarks", "label": "Audit Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "System or user note explaining why this balance changed."},
        ],
        datatable_columns=_ledger_columns,
        reset_defaults={"year": timezone.localdate().year},
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "leave_type__name",
            "change_type",
        ],
    )
)


register_entity(
    EntityConfig(
        name="leave_accrual",
        url_path="leave-accruals",
        verbose_name="Leave Accrual",
        model=LeaveAccrual,
        form_class=LeaveAccrualForm,
        datatable_view=LeaveAccrualDataTableView,
        fields=[
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "leave_type", "label": "Leave Type", "type": "select", "required": True, "col": 6, "url_name": "leave_type_select"},
            {"name": "accrual_date", "label": "Accrual Date", "type": "date", "required": True, "col": 6},
            {"name": "days_added", "label": "Days Added", "type": "number", "required": True, "col": 6, "placeholder": "e.g. 1.50"},
            {"name": "remarks", "label": "Accrual Notes", "type": "textarea", "required": False, "col": 12, "placeholder": "Monthly accrual, opening adjustment, or policy-driven grant."},
        ],
        datatable_columns=_accrual_columns,
        reset_defaults={"accrual_date": timezone.localdate().isoformat()},
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "leave_type__name",
        ],
    )
)
