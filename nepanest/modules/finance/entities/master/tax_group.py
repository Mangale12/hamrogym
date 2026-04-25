from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from ...datatables.tax_group_data_table import TaxGroupDataTableView
from ...forms import TaxGroupForm
from ...models import TaxGroup, TaxGroupItem


TAX_GROUP_ITEMS_SECTION = {
    "title": "Tax Group Items",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "tax",
            "label": "Tax",
            "type": "select",
            "required": True,
            "url_name": "tax_select",
        },
        {
            "name": "sequence",
            "label": "Sequence",
            "type": "number",
            "required": True,
            "min": 1,
        },
        {
            "name": "override_rate",
            "label": "Override Rate %",
            "type": "number",
            "required": False,
            "min": 0,
        },
        {
            "name": "is_compound",
            "label": "Compound",
            "type": "checkbox",
            "required": False,
        },
        {
            "name": "remarks",
            "label": "Remarks",
            "type": "text",
            "required": False,
        },
    ],
}

TAX_GROUP_ITEMS_RELATION = RelatedDynamicSectionConfig(
    section_name="items",
    related_model=TaxGroupItem,
    parent_field="tax_group",
    fields=["tax", "sequence", "override_rate", "is_compound", "remarks"],
    required_fields=["tax"],
    bool_fields=["is_compound"],
    empty_check_fields=["tax", "sequence", "override_rate", "remarks"],
    save_transformers={
        "tax": lambda value: (value or "").strip(),
        "sequence": lambda value: int(value) if str(value or "").strip().isdigit() else 1,
        "remarks": lambda value: (value or "").strip(),
    },
)

_save_tax_group_items = build_related_section_saver(TAX_GROUP_ITEMS_RELATION)
_load_tax_group_items = build_related_section_loader(TAX_GROUP_ITEMS_RELATION)


register_entity(
    EntityConfig(
        name="tax_group",
        url_path="tax-groups",
        verbose_name="Tax Group",
        model=TaxGroup,
        form_class=TaxGroupForm,
        datatable_view=TaxGroupDataTableView,
        fields=[],
        tabs=[
            {
                "key": "basic",
                "label": "Basic",
                "fields": [
                    {"name": "code", "label": "Code", "type": "text", "required": True, "col": 4, "placeholder": "SALES-TAX"},
                    {"name": "name", "label": "Name", "type": "text", "required": True, "col": 5, "placeholder": "Sales Taxes"},
                    {"name": "application_scope", "label": "Application Scope", "type": "static_select", "required": True, "col": 3, "options": TaxGroup._meta.get_field("application_scope").choices},
                    {"name": "is_default", "label": "Default", "type": "checkbox", "required": False, "col": 3},
                    {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 3, "default": True},
                    {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
                ],
            },
            {
                "key": "items",
                "label": "Items",
                "requires_id": True,
                "fields": [],
                "sections": ["items"],
            },
        ],
        dynamic_sections={"items": TAX_GROUP_ITEMS_SECTION},
        dynamic_sections_loader=_load_tax_group_items,
        dynamic_sections_saver=_save_tax_group_items,
        datatable_columns=[
            {"name": "code", "title": "Code"},
            {"name": "name", "title": "Name"},
            {"name": "application_scope", "title": "Scope"},
            {"name": "is_default", "title": "Default", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
        ],
        reset_defaults={"application_scope": "both", "is_active": True},
        select_search_fields=["code", "name"],
        select_label_func=lambda obj: f"{obj.code} - {obj.name}",
    )
)
