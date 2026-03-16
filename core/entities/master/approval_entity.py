from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.approval_entity_data_table import ApprovalEntityDataTableView, APPROVAL_ENTITY_COLUMNS
from ...forms.approval_entity_form import ApprovalEntityForm
from ...models import ApprovalEntity


register_entity(
    EntityConfig(
        name="approval_entity",
        url_path="approval-entities",
        verbose_name="Approval Entity",
        model=ApprovalEntity,
        form_class=ApprovalEntityForm,
        datatable_view=ApprovalEntityDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in APPROVAL_ENTITY_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
