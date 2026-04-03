from core.config import EntityConfig
from core.choices import get_month_choices
from core.helpers.helper import get_calendar_type
from core.registry import register_entity

from ...datatables.payroll_data_table import PayrollRunDataTableView
from ...forms.payroll_form import PayrollRunForm
from ...models import PayrollRun
from .payroll_shared import (
    approve_payroll_action,
    build_attendance_inputs_action,
    build_leave_inputs_action,
    lock_payroll_action,
    payroll_run_columns,
    process_payroll_action,
    reset_payroll_action,
    today,
)


def _payroll_month_options(request=None):
    return get_month_choices(get_calendar_type(request))


register_entity(
    EntityConfig(
        name="payroll_run",
        url_path="payroll-runs",
        verbose_name="Payroll Run",
        model=PayrollRun,
        form_class=PayrollRunForm,
        datatable_view=PayrollRunDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "required": False, "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "currency", "label": "Currency", "type": "select", "required": False, "col": 4, "url_name": "currency_select"},
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": True, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "name", "label": "Run Name", "type": "text", "required": True, "col": 4, "placeholder": "March 2026 Monthly Payroll"},
            {"name": "payroll_month", "label": "Payroll Month", "type": "static_select", "required": True, "col": 2, "options": _payroll_month_options},
            {"name": "period_start", "label": "Period Start", "type": "date", "required": True, "col": 2},
            {"name": "period_end", "label": "Period End", "type": "date", "required": True, "col": 2},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Optional run note, cutoff note, or approval comment."},
        ],
        row_actions={
            "build_attendance_inputs": build_attendance_inputs_action,
            "build_leave_inputs": build_leave_inputs_action,
            "process": process_payroll_action,
            "reset_run": reset_payroll_action,
            "approve_run": approve_payroll_action,
            "lock_run": lock_payroll_action,
        },
        action_state_field="status",
        hide_edit_on_values=["approved", "locked"],
        hide_delete_on_values=["processed", "reviewed", "approved", "locked"],
        action_buttons=[
            {
                "action_name": "build_attendance_inputs",
                "title": "Build Attendance Inputs",
                "label": "",
                "icon_class": "fas fa-clipboard-list",
                "class_name": "btn-outline-primary",
                "confirm_text": "Rebuild attendance payroll inputs for this payroll run?",
                "success_message": "Attendance payroll inputs rebuilt successfully.",
                "hide_on_values": ["approved", "locked"],
            },
            {
                "action_name": "build_leave_inputs",
                "title": "Build Leave Inputs",
                "label": "",
                "icon_class": "fas fa-calendar-minus",
                "class_name": "btn-outline-info",
                "confirm_text": "Rebuild leave payroll impacts for this payroll run?",
                "success_message": "Leave payroll impacts rebuilt successfully.",
                "hide_on_values": ["approved", "locked"],
            },
            {
                "action_name": "process",
                "title": "Process Payroll",
                "label": "",
                "icon_class": "fas fa-play",
                "class_name": "btn-outline-success",
                "confirm_text": "Process this payroll run now?",
                "success_message": "Payroll run processed successfully.",
                "hide_on_values": ["approved", "locked"],
            },
            {
                "action_name": "reset_run",
                "title": "Reset To Draft",
                "label": "",
                "icon_class": "fas fa-undo",
                "class_name": "btn-outline-warning",
                "confirm_text": "Reset this payroll run to draft and remove processed rows?",
                "success_message": "Payroll run reset to draft successfully.",
                "hide_on_values": ["draft", "approved", "locked"],
            },
            {
                "action_name": "approve_run",
                "title": "Approve Payroll",
                "label": "",
                "icon_class": "fas fa-check",
                "class_name": "btn-outline-primary",
                "confirm_text": "Approve this payroll run?",
                "success_message": "Payroll run approved successfully.",
                "hide_on_values": ["draft", "approved", "locked"],
            },
            {
                "action_name": "lock_run",
                "title": "Lock Payroll",
                "label": "",
                "icon_class": "fas fa-lock",
                "class_name": "btn-outline-dark",
                "confirm_text": "Lock this payroll run? This will prevent recalculation.",
                "success_message": "Payroll run locked successfully.",
                "hide_on_values": ["draft", "processed", "reviewed", "locked"],
            },
        ],
        datatable_columns=payroll_run_columns,
        reset_defaults={
            "payroll_month": today.month,
            "period_start": today.replace(day=1).isoformat(),
            "period_end": today.isoformat(),
        },
        select_search_fields=["name", "status", "fiscal_year__name"],
    )
)
