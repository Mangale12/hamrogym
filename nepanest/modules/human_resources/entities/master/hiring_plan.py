from __future__ import annotations

from core.config import EntityConfig
from core.registry import register_entity

from nepanest.modules.recruitment.datatables import (
    HIRING_PLAN_COLUMNS,
    HiringPlanDataTableView,
)
from nepanest.modules.recruitment.forms import HiringPlanForm
from nepanest.modules.recruitment.models import HiringPlan, HiringPlanItem
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

ITEMS_SECTION = {
    "title": "Hiring Plan Items",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "branch",
            "label": "Branch",
            "type": "select",
            "required": True,
            "url_name": "branch_select",
        },
        {
            "name": "department",
            "label": "Department",
            "type": "select",
            "required": True,
            "url_name": "department_select",
        },
        {
            "name": "designation",
            "label": "Designation",
            "type": "select",
            "required": True,
            "url_name": "designation_select",
        },
        {
            "name": "employeement_type",
            "label": "Employment Type",
            "type": "select",
            "required": True,
            "url_name": "employeement_type_select",
        },
        {
            "name": "planned_head_count",
            "label": "Head Count",
            "type": "number",
            "required": True,
            "min": 1,
        },
        {
            "name": "planned_month",
            "label": "Planned Month",
            "type": "number",
            "required": True,
            "min": 1,
        },
        {
            "name": "remarks",
            "label": "Remarks",
            "type": "text",
            "required": False,
        },
    ],
}

ITEMS_SECTION_RELATION = RelatedDynamicSectionConfig(
    section_name="items",
    related_model=HiringPlanItem,
    parent_field="hiring_plan",
    fields=["branch", "department", "designation", "employeement_type", "planned_head_count", "planned_month", "remarks"],
    required_fields=["branch", "department", "designation", "employeement_type", "planned_head_count", "planned_month"],
    bool_fields=[],
    empty_check_fields=["branch", "department", "designation", "employeement_type", "planned_head_count", "planned_month", "remarks"],
    save_transformers={
        "branch": lambda value: (value or "").strip(),
        "department": lambda value: (value or "").strip(),
        "designation": lambda value: (value or "").strip(),
        "employeement_type": lambda value: (value or "").strip(),
        "planned_head_count": lambda value: max(1, _to_int(value)),
        "planned_month": lambda value: max(1, _to_int(value)),
        "remarks": lambda value: (value or "").strip(),
    },
)

_save_hiring_plan_items = build_related_section_saver(ITEMS_SECTION_RELATION)
_load_hiring_plan_items = build_related_section_loader(ITEMS_SECTION_RELATION)


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


register_entity(
    EntityConfig(
        name="hiring_plan",
        url_path="hiring-plans",
        verbose_name="Hiring Plan",
        model=HiringPlan,
        form_class=HiringPlanForm,
        datatable_view=HiringPlanDataTableView,
        fields=[
            {
                "name": "name",
                "label": "Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Annual Hiring Plan",
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "HP-001",
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": HiringPlan._meta.get_field("status").choices,
            },
            {
                "name": "description",
                "label": "Description",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
            {
                "name": "is_active",
                "label": "Active",
                "type": "checkbox",
                "required": False,
                "col": 6,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        dynamic_sections={
            "items": ITEMS_SECTION,
        },
        dynamic_sections_loader=_load_hiring_plan_items,
        dynamic_sections_saver=_save_hiring_plan_items,
        datatable_columns=[
            {
                "name": key,
                "title": key.replace("_", " ").title(),
                "render": "function(data){return data ? 'Yes' : 'No';}"
                if key == "is_active"
                else None,
            }
            for key, _accessor in HIRING_PLAN_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True, "status": "draft"},
    )
)
