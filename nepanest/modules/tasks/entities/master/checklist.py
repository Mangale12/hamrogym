from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)
from nepanest.modules.projects.datatables import CHECKLIST_COLUMNS, ChecklistDataTableView
from nepanest.modules.projects.forms import ChecklistForm
from nepanest.modules.projects.models import Checklist, ChecklistItem

CHECKLIST_ITEM_SECTION = {
    "title": "Checklist Items",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "name", "label": "Name", "type": "text", "required": True},
        {"name": "order", "label": "Order", "type": "number", "required": True},
        {"name": "is_required", "label": "Is Required", "type": "checkbox", "required": False},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False}
    ],
}

CHECKLIST_ITEM_RELATION = RelatedDynamicSectionConfig(
    section_name="checklist_items",
    related_model=ChecklistItem,
    parent_field="checklist",
    fields=["name", "order", "is_required", "remarks"],
    required_fields=["name", "order"],
    bool_fields=["is_required"],
    empty_check_fields=["name", "order"],
    order_by="order",
    save_transformers={
        "name": lambda value: (value or "").strip(),
        "order": lambda value: int(value) if str(value).strip() else 0,
    },
)

_save_checklist_item = build_related_section_saver(CHECKLIST_ITEM_RELATION)
_load_checklist_item = build_related_section_loader(CHECKLIST_ITEM_RELATION)

register_entity(
    EntityConfig(
        name="checklist",
        url_path="checklists",
        verbose_name="Task Checklist",
        model=Checklist,
        form_class=ChecklistForm,
        datatable_view=ChecklistDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "project_id", "label": "Project", "type": "select", "required": False, "col": 6, "url_name": "project_select"},
            {"name": "module_id", "label": "Module", "type": "select", "required": False, "col": 6, "url_name": "task_module_select"},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        dynamic_sections={
            "checklist_items": CHECKLIST_ITEM_SECTION
        },
        dynamic_sections_loader=_load_checklist_item,
        dynamic_sections_saver=_save_checklist_item,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in CHECKLIST_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
