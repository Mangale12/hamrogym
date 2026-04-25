from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity
from nepanest.modules.leave.datatables import LEAVE_REQUEST_COLUMNS, LeaveRequestDataTableView
from nepanest.modules.leave.forms import LeaveRequestForm
from nepanest.modules.leave.models import LeaveRequest
from nepanest.modules.leave.services import (
    approve_leave_request,
    cancel_leave_request,
    prepare_leave_request,
    reject_leave_request,
    sync_leave_request_values,
)


APPROVAL_HISTORY_SECTION = {
    "title": "Approval History",
    "layout": "table",
    "allow_add": False,
    "allow_remove": False,
    "fields": [
        {"name": "level", "label": "Level", "type": "text", "readonly": True},
        {"name": "approver_name", "label": "Approver", "type": "text", "readonly": True},
        {"name": "status", "label": "Status", "type": "text", "readonly": True},
        {"name": "action_at_display", "label": "Action At", "type": "text", "readonly": True},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "readonly": True},
    ],
}

_request_datatable_columns = [
    {"name": "employee", "title": "Employee"},
    {"name": "leave_type", "title": "Leave Type"},
    {"name": "start_date", "title": "From"},
    {"name": "end_date", "title": "To"},
    {"name": "total_days", "title": "Days"},
    {
        "name": "status",
        "title": "Status",
        "render": (
            "function(data){"
            "const map={approved:'success',pending:'warning',rejected:'danger',cancelled:'secondary'};"
            "const cls=map[data]||'light';"
            "const label=(data||'').replace('_',' ');"
            "return `<span class=\"badge bg-${cls}\">${label}</span>`;"
            "}"
        ),
    },
    {"name": "applied_at", "title": "Applied At"},
    {"name": "approved_at", "title": "Approved At"},
]


def _load_leave_request_sections(leave_request: LeaveRequest):
    rows = []
    for approval in leave_request.approvals.select_related("approver").order_by("level", "id"):
        rows.append(
            {
                "id": approval.id,
                "level": approval.level,
                "approver_name": approval.approver.get_full_name() or approval.approver.username,
                "status": approval.status,
                "action_at_display": approval.action_at.strftime("%Y-%m-%d %H:%M") if approval.action_at else "",
                "remarks": approval.remarks,
            }
        )
    return {"approval_history": rows}


def _pre_save_leave_request(_request, leave_request: LeaveRequest) -> None:
    sync_leave_request_values(leave_request)
    if leave_request.status not in {"approved", "rejected", "cancelled"}:
        leave_request.status = "pending"


def _post_save_leave_request(_request, leave_request: LeaveRequest) -> None:
    prepare_leave_request(leave_request=leave_request)
    leave_request.save(update_fields=["status", "updated_at"])


def _approve_leave_request(request, leave_request: LeaveRequest):
    result = approve_leave_request(leave_request=leave_request, acting_user=request.user, request=request)
    if result.get("finalized"):
        return {"message": "Leave request fully approved successfully."}
    return {"message": f"Level {result.get('level')} approved. Forwarded to level {result.get('next_level')}."}


def _reject_leave_request(request, leave_request: LeaveRequest):
    reject_leave_request(leave_request=leave_request, acting_user=request.user)
    return {"message": "Leave request rejected successfully."}


def _cancel_leave_request(request, leave_request: LeaveRequest):
    cancel_leave_request(leave_request=leave_request)
    return {"message": "Leave request cancelled successfully."}


register_entity(
    EntityConfig(
        name="leave_request",
        url_path="leave-requests",
        verbose_name="Leave Request",
        model=LeaveRequest,
        form_class=LeaveRequestForm,
        datatable_view=LeaveRequestDataTableView,
        fields=[],
        tabs=[
            {
                "key": "request",
                "label": "Request Details",
                "fields": [
                    {
                        "name": "employee",
                        "label": "Employee",
                        "type": "select",
                        "required": True,
                        "col": 6,
                        "url_name": "employee_select",
                    },
                    {
                        "name": "leave_type",
                        "label": "Leave Type",
                        "type": "select",
                        "required": True,
                        "col": 6,
                        "url_name": "leave_type_select",
                    },
                    {
                        "name": "start_date",
                        "label": "Start Date",
                        "type": "date",
                        "required": True,
                        "col": 4,
                        "placeholder": "Select start date",
                    },
                    {
                        "name": "end_date",
                        "label": "End Date",
                        "type": "date",
                        "required": True,
                        "col": 4,
                        "placeholder": "Select end date",
                    },
                    {
                        "name": "is_half_day",
                        "label": "Half Day Request",
                        "type": "checkbox",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "half_day_type",
                        "label": "Half Day Slot",
                        "type": "static_select",
                        "required": False,
                        "col": 6,
                        "options": LeaveRequest._meta.get_field("half_day_type").choices,
                    },
                    {
                        "name": "attachment",
                        "label": "Supporting Attachment",
                        "type": "file",
                        "required": False,
                        "col": 6,
                    },
                    {
                        "name": "reason",
                        "label": "Business Reason",
                        "type": "textarea",
                        "required": True,
                        "col": 12,
                        "placeholder": "Explain the leave request clearly for approvers and audit history.",
                    },
                ],
            },
            {
                "key": "approvals",
                "label": "Approval Trail",
                "fields": [],
                "requires_id": True,
                "sections": ["approval_history"],
            },
        ],
        dynamic_sections={
            "approval_history": APPROVAL_HISTORY_SECTION,
        },
        dynamic_sections_loader=_load_leave_request_sections,
        pre_save=_pre_save_leave_request,
        post_save=_post_save_leave_request,
        row_actions={
            "approve": _approve_leave_request,
            "reject": _reject_leave_request,
            "cancel": _cancel_leave_request,
        },
        action_state_field="status",
        hide_edit_on_values=["approved", "rejected", "cancelled"],
        hide_delete_on_values=["approved"],
        action_buttons=[
            {
                "action_name": "approve",
                "title": "Approve Leave",
                "label": "",
                "icon_class": "fas fa-check",
                "class_name": "btn-outline-success",
                "confirm_text": "Approve this leave request?",
                "success_message": "Leave request approved successfully.",
                "hide_on_values": ["approved", "rejected", "cancelled"],
            },
            {
                "action_name": "reject",
                "title": "Reject Leave",
                "label": "",
                "icon_class": "fas fa-times",
                "class_name": "btn-outline-danger",
                "confirm_text": "Reject this leave request?",
                "success_message": "Leave request rejected successfully.",
                "hide_on_values": ["approved", "rejected", "cancelled"],
            },
            {
                "action_name": "cancel",
                "title": "Cancel Leave",
                "label": "",
                "icon_class": "fas fa-ban",
                "class_name": "btn-outline-warning",
                "confirm_text": "Cancel this leave request?",
                "success_message": "Leave request cancelled successfully.",
                "hide_on_values": ["cancelled", "rejected"],
            },
        ],
        datatable_columns=_request_datatable_columns,
        reset_defaults={
            "start_date": timezone.localdate().isoformat(),
            "end_date": timezone.localdate().isoformat(),
        },
    )
)
