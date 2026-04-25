from core.config import EntityConfig
from core.registry import register_entity
from nepanest.modules.recruitment.datatables import (
    APPROVAL_WORKFLOW_LEVEL_COLUMNS,
    ApprovalWorkflowLevelDataTableView,
)
from nepanest.modules.recruitment.forms import ApprovalWorkflowLevelForm
from nepanest.modules.recruitment.models import ApprovalWorkflowLevel


register_entity(
    EntityConfig(
        name="approval_workflow_level",
        url_path="approval-workflow-levels",
        verbose_name="Approval Workflow Level",
        model=ApprovalWorkflowLevel,
        form_class=ApprovalWorkflowLevelForm,
        datatable_view=ApprovalWorkflowLevelDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in APPROVAL_WORKFLOW_LEVEL_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
