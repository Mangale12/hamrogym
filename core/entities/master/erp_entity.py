from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.erp_entity_data_table import ErpEntityDataTableView, ERP_ENTITY_COLUMNS
from ...forms.erp_entity_form import ErpEntityForm
from ...models import ErpEntity


register_entity(
    EntityConfig(
        name="erp_entity",
        url_path="erp-entities",
        verbose_name="ERP Entity",
        model=ErpEntity,
        form_class=ErpEntityForm,
        datatable_view=ErpEntityDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "module", "label": "Module", "type": "text", "required": True, "col": 6},
            {"name": "app_label", "label": "App Label", "type": "text", "required": True, "col": 6},
            {"name": "model_name", "label": "Model Name", "type": "text", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ERP_ENTITY_COLUMNS
            if key != "id"
        ],
        show_actions=False,
        show_create=False,
        reset_defaults={},
    )
)
