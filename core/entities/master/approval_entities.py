from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.approval_entities_data_table import ApprovalEntityDataTableView, APPROVAL_ENTITIES_COLUMNS
from ...forms.approval_entities_form import ApprovalEntityForm
from ...models import ApprovalEntity


register_entity(
    EntityConfig(
        name="approval_entities",
        url_path="approval-entities",
        verbose_name="Approval Entity",
        model=ApprovalEntity,
        form_class=ApprovalEntityForm,
        datatable_view=ApprovalEntityDataTableView,
        fields=[
            {"name": "erp_entity", "label": "ERP Entity", "type": "select", "required": True, "col": 6, "url_name" : "erp_entity_select"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in APPROVAL_ENTITIES_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
