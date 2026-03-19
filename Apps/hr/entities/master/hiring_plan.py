from __future__ import annotations

import re
from typing import Dict, List

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.hiring_plan_data_table import (
    HIRING_PLAN_COLUMNS,
    HiringPlanDataTableView,
)
from ...forms.hiring_plan_form import HiringPlanForm
from ...models import HiringPlan, HiringPlanItem


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


def _parse_dynamic_section(request, section_name: str) -> List[Dict[str, object]]:
    pattern = re.compile(rf"^{re.escape(section_name)}\[(\d+)\]\[(.+)\]$")
    rows: Dict[int, Dict[str, object]] = {}

    for key, value in request.POST.items():
        match = pattern.match(key)
        if not match:
            continue
        index = int(match.group(1))
        field = match.group(2)
        rows.setdefault(index, {})[field] = value

    return [rows[idx] for idx in sorted(rows.keys())]


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _save_hiring_plan_items(request, hiring_plan: HiringPlan) -> None:
    rows = _parse_dynamic_section(request, "items")
    existing = {item.id: item for item in HiringPlanItem.objects.filter(hiring_plan=hiring_plan)}
    keep_ids = []

    for row in rows:
        item_id = row.get("id")
        item = None
        if item_id and str(item_id).isdigit():
            item = existing.get(int(item_id))

        if not item:
            item = HiringPlanItem(hiring_plan=hiring_plan)

        branch_id = row.get("branch")
        department_id = row.get("department")
        designation_id = row.get("designation")
        employeement_type_id = row.get("employeement_type")

        if not any(
            [
                branch_id,
                department_id,
                designation_id,
                employeement_type_id,
                row.get("planned_head_count"),
                row.get("planned_month"),
                row.get("remarks"),
            ]
        ):
            continue

        if not all([branch_id, department_id, designation_id, employeement_type_id]):
            continue

        item.branch_id = branch_id
        item.department_id = department_id
        item.designation_id = designation_id
        item.employeement_type_id = employeement_type_id
        item.planned_head_count = max(1, _to_int(row.get("planned_head_count"), default=1))
        item.planned_month = max(1, _to_int(row.get("planned_month"), default=1))
        item.remarks = (row.get("remarks") or "").strip()
        item.save()
        keep_ids.append(item.id)

    queryset = HiringPlanItem.objects.filter(hiring_plan=hiring_plan)
    if keep_ids:
        queryset.exclude(id__in=keep_ids).delete()
    else:
        queryset.delete()


def _load_hiring_plan_items(hiring_plan: HiringPlan) -> Dict[str, List[Dict[str, object]]]:
    return {
        "items": [
            {
                "id": item.id,
                "branch": str(item.branch_id or ""),
                "department": str(item.department_id or ""),
                "designation": str(item.designation_id or ""),
                "employeement_type": str(item.employeement_type_id or ""),
                "planned_head_count": item.planned_head_count,
                "planned_month": item.planned_month,
                "remarks": item.remarks or "",
            }
            for item in hiring_plan.items.select_related(
                "branch",
                "department",
                "designation",
                "employeement_type",
            ).order_by("id")
        ]
    }


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
