from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.asset_assignment_data_table import (
    ASSET_ASSIGNMENT_COLUMNS,
    AssetAssignmentDataTableView,
)
from ...forms.asset_assignment_form import AssetAssignmentForm
from ...models import AssetAssignment
 

def _prepare_asset_assignment(request, assignment: AssetAssignment) -> None:
    if not assignment.assigned_by_id:
        assignment.assigned_by = request.user
    if assignment.status == AssetAssignment.STATUS_ACTIVE:
        assignment.return_date = None
        assignment.received_by = None
        assignment.condition_at_return = None
    elif assignment.status == AssetAssignment.STATUS_RETURNED and not assignment.received_by_id:
        assignment.received_by = request.user


register_entity(
    EntityConfig(
        name="asset_assignment",
        url_path="asset-assignments",
        verbose_name="Asset Assignment",
        model=AssetAssignment,
        form_class=AssetAssignmentForm,
        datatable_view=AssetAssignmentDataTableView,
        template_name="assets/asset_assignment_index.html",
        fields=[],
        tabs=[
            {
                "key": "issue",
                "label": "Issue",
                "fields": [
                    {"name": "asset", "label": "Asset", "type": "select", "required": True, "col": 6, "url_name": "asset_select"},
                    {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
                    {"name": "assigned_date", "label": "Assigned Date", "type": "date", "required": True, "col": 4},
                    {"name": "expected_return_date", "label": "Expected Return Date", "type": "date", "required": False, "col": 4},
                    {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 4, "options": AssetAssignment.STATUS_CHOICES},
                    {"name": "assigned_by", "label": "Assigned By", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
                    {"name": "condition_at_issue", "label": "Condition At Issue", "type": "select", "required": False, "col": 6, "url_name": "asset_condition_select"},
                    {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
                ],
            },
            {
                "key": "return",
                "label": "Return",
                "requires_id": True,
                "fields": [
                    {"name": "return_date", "label": "Return Date", "type": "date", "required": False, "col": 4},
                    {"name": "received_by", "label": "Received By", "type": "select", "required": False, "col": 4, "url_name": "user_select"},
                    {"name": "condition_at_return", "label": "Condition At Return", "type": "select", "required": False, "col": 4, "url_name": "asset_condition_select"},
                    {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
                ],
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_ASSIGNMENT_COLUMNS
            if key != "id"
        ],
        pre_save=_prepare_asset_assignment,
        reset_defaults={"status": AssetAssignment.STATUS_ACTIVE},
        action_state_field="status",
        action_buttons=[
            {
                "title": "Return Asset",
                "label": "",
                "icon_class": "fas fa-undo",
                "class_name": "btn-outline-warning",
                "tab_key": "return",
                "hide_on_values": [AssetAssignment.STATUS_RETURNED],
            },
        ],
        select_search_fields=[
            "asset__name",
            "asset__code",
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "status",
        ],
        hide_delete_on_values=[AssetAssignment.STATUS_RETURNED],
    )
)
