from core.datatables.views import BaseDataTableView
from ..models import ApprovalWorkflowLevel


APPROVAL_WORKFLOW_LEVEL_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class ApprovalWorkflowLevelDataTableView(BaseDataTableView):
    model = ApprovalWorkflowLevel
    columns = APPROVAL_WORKFLOW_LEVEL_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
