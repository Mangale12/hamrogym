from django.core.exceptions import ValidationError

from core.config import EntityConfig
from core.registry import register_entity
from ...services import sync_asset_status_from_incident
from ...datatables.asset_incident_data_table import AssetIncidentDataTableView, ASSET_INCIDENT_COLUMNS
from ...forms.asset_incident_form import AssetIncidentForm
from ...models import AssetIncident, AssetMaintenanceRecord
from core.choices import ASSET_INCIDENT_STATUS_CHOICES as STATUS_CHOICES


def _prepare_asset_incident(request, incident: AssetIncident) -> None:
    if not incident.reported_by_id:
        incident.reported_by = request.user


def _transition_incident(incident: AssetIncident, *, status: str, approved_by=None) -> None:
    incident.status = status
    if approved_by is not None:
        incident.approved_by = approved_by
    incident.save(update_fields=["status", "approved_by", "updated_at"])


def _assert_incident_status(incident: AssetIncident, allowed_statuses, message: str) -> None:
    if incident.status not in allowed_statuses:
        raise ValidationError(message)


def _create_maintenance_from_incident(request, incident: AssetIncident) -> None:
    if not incident.incident_type.auto_create_maintenance:
        return

    defaults = {
        "asset": incident.asset,
        "maintenance_date": incident.incident_date,
        "maintenance_type": incident.incident_type.name,
        "cost": incident.estimated_cost,
        "performed_by": request.user,
        "status": AssetMaintenanceRecord.STATUS_PENDING,
        "remarks": f"Auto-created from incident #{incident.pk}. {incident.remarks}".strip(),
    }
    AssetMaintenanceRecord.objects.get_or_create(
        incident=incident,
        defaults=defaults,
    )


def _submit_incident(request, incident: AssetIncident):
    _assert_incident_status(incident, {"draft"}, "Only draft incidents can be submitted.")
    _transition_incident(incident, status="reported")
    return {"message": "Incident submitted successfully."}


def _review_incident(request, incident: AssetIncident):
    _assert_incident_status(incident, {"reported"}, "Only reported incidents can move to under review.")
    _transition_incident(incident, status="under_review")
    return {"message": "Incident moved to under review."}


def _approve_incident(request, incident: AssetIncident):
    _assert_incident_status(incident, {"under_review"}, "Only incidents under review can be approved.")
    _transition_incident(incident, status="approved", approved_by=request.user)
    _create_maintenance_from_incident(request, incident)
    sync_asset_status_from_incident(incident)
    return {"message": "Incident approved successfully."}


def _reject_incident(request, incident: AssetIncident):
    _assert_incident_status(incident, {"under_review"}, "Only incidents under review can be rejected.")
    _transition_incident(incident, status="rejected", approved_by=request.user)
    return {"message": "Incident rejected successfully."}


def _resolve_incident(request, incident: AssetIncident):
    _assert_incident_status(incident, {"approved"}, "Only approved incidents can be resolved.")
    _transition_incident(incident, status="resolved", approved_by=incident.approved_by or request.user)
    sync_asset_status_from_incident(incident)
    return {"message": "Incident resolved successfully."}


def _close_incident(request, incident: AssetIncident):
    _assert_incident_status(incident, {"resolved", "rejected"}, "Only resolved or rejected incidents can be closed.")
    _transition_incident(incident, status="closed", approved_by=incident.approved_by or request.user)
    return {"message": "Incident closed successfully."}


register_entity(
    EntityConfig(
        name="asset_incident",
        url_path="asset-incidents",
        verbose_name="Asset Incident",
        model=AssetIncident,
        form_class=AssetIncidentForm,
        datatable_view=AssetIncidentDataTableView,
        fields=[
            {"name": "asset", "label": "Asset", "type": "select", "required": True, "col": 6, "url_name": "asset_select"},
            {"name": "employee", "label": "User", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
            {"name": "incident_type", "label": "Incident Type", "type": "select", "required": True, "col": 6, "url_name": "asset_incident_type_select"},
            {"name": "incident_date", "label": "Incident Date", "type": "date", "required": True, "col": 6},
            {"name": "estimated_cost", "label": "Estimated Cost", "type": "number", "required": False, "col": 4},
            {"name": "final_cost", "label": "Final Cost", "type": "number", "required": False, "col": 4},
            {"name": "approval_deduction_cost", "label": "Approval Deduction Cost", "type": "number", "required": False, "col": 4},
            {"name": "reported_by", "label": "Reported By", "type": "select", "required": False, "col": 4, "url_name": "user_select"},
            {"name": "approved_by", "label": "Approved By", "type": "select", "required": False, "col": 4, "url_name": "user_select"},
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": True, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": True, "col": 6, "url_name": "branch_select"},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 6, "options" : STATUS_CHOICES},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_INCIDENT_COLUMNS
            if key != "id"
        ],
        pre_save=_prepare_asset_incident,
        row_actions={
            "submit": _submit_incident,
            "review": _review_incident,
            "approve": _approve_incident,
            "reject": _reject_incident,
            "resolve": _resolve_incident,
            "close": _close_incident,
        },
        action_state_field="status",
        hide_edit_on_values=["approved", "resolved", "closed"],
        hide_delete_on_values=["approved", "resolved", "closed"],
        reset_defaults={"status": "draft"},
        action_buttons=[
            {
                "action_name": "submit",
                "title": "Submit",
                "icon_class": "fas fa-paper-plane",
                "class_name": "btn-outline-primary",
                "confirm_text": "Submit this incident?",
                "success_message": "Incident submitted successfully.",
                "hide_on_values": ["reported", "under_review", "approved", "rejected", "resolved", "closed"],
            },
            {
                "action_name": "review",
                "title": "Review",
                "icon_class": "fas fa-search",
                "class_name": "btn-outline-info",
                "confirm_text": "Move this incident to under review?",
                "success_message": "Incident moved to under review.",
                "hide_on_values": ["draft", "under_review", "approved", "rejected", "resolved", "closed"],
            },
            {
                "action_name": "approve",
                "title": "Approve",
                "icon_class": "fas fa-check",
                "class_name": "btn-outline-success",
                "confirm_text": "Approve this incident?",
                "success_message": "Incident approved successfully.",
                "hide_on_values": ["draft", "reported", "approved", "rejected", "resolved", "closed"],
            },
            {
                "action_name": "reject",
                "title": "Reject",
                "icon_class": "fas fa-times",
                "class_name": "btn-outline-danger",
                "confirm_text": "Reject this incident?",
                "success_message": "Incident rejected successfully.",
                "hide_on_values": ["draft", "reported", "approved", "rejected", "resolved", "closed"],
            },
            {
                "action_name": "resolve",
                "title": "Resolve",
                "icon_class": "fas fa-check-double",
                "class_name": "btn-outline-success",
                "confirm_text": "Mark this incident as resolved?",
                "success_message": "Incident resolved successfully.",
                "hide_on_values": ["draft", "reported", "under_review", "rejected", "resolved", "closed"],
            },
            {
                "action_name": "close",
                "title": "Close",
                "icon_class": "fas fa-lock",
                "class_name": "btn-outline-secondary",
                "confirm_text": "Close this incident?",
                "success_message": "Incident closed successfully.",
                "hide_on_values": ["draft", "reported", "under_review", "approved", "closed"],
            },
        ],
        select_search_fields=[
            "asset__name",
            "asset__code",
            "incident_type__name",
            "employee__first_name",
            "employee__last_name",
            "employee__username",
            "status",
        ],
    )
)
