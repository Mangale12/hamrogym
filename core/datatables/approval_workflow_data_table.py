from core.datatables.views import BaseDataTableView
from ..models import ApprovalWorkflow


APPROVAL_WORKFLOW_COLUMNS = [
    ("id", "id"),
    ("entity", "entity.name"),
    ("name", "name"),
    ("code", "code"),
    ("description", "description"),
    ("priority", "priority"),
    ("version", "version"),
    ("is_default", "is_default"),
    ("effective_from", "effective_from"),
    ("effective_to", "effective_to"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class ApprovalWorkflowDataTableView(BaseDataTableView):
    model = ApprovalWorkflow
    columns = APPROVAL_WORKFLOW_COLUMNS
    searchable_columns = [
        "entity__name",
        "name",
        "code",
        "description",
        "priority",
        "version",
        "is_default",
        "effective_from",
        "effective_to",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "entity__name",
        "name",
        "code",
        "description",
        "priority",
        "version",
        "is_default",
        "effective_from",
        "effective_to",
        "is_active",
        "remarks",
    ]
