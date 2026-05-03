from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from ...datatables.membership_plan_data_table import MEMBERSHIP_PLAN_COLUMNS, MembershipPlanDataTableView
from ...forms.membership_plan_form import MembershipPlanForm
from ...models import MembershipPlan, MembershipRestriction


RESTRICTION_SECTION = {
    "title": "Restrictions",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "restriction_type",
            "label": "Type",
            "type": "static_select",
            "required": True,
            "options": [("", "Select Type"), *MembershipRestriction.RestrictionType.choices],
        },
        {
            "name": "value",
            "label": "Value",
            "type": "text",
            "required": True,
        },
    ],
}

RESTRICTION_RELATION = RelatedDynamicSectionConfig(
    section_name="restrictions",
    related_model=MembershipRestriction,
    parent_field="membership_plan",
    fields=["restriction_type", "value"],
    required_fields=["restriction_type", "value"],
    empty_check_fields=["restriction_type", "value"],
    save_transformers={
        "restriction_type": lambda value: (value or "").strip(),
        "value": lambda value: (value or "").strip(),
    },
)

_load_restrictions = build_related_section_loader(RESTRICTION_RELATION)


def _save_restrictions(request, membership_plan):
    active_tab = (request.POST.get("_active_tab") or "").strip()
    if active_tab in {"", "restrictions"}:
        build_related_section_saver(RESTRICTION_RELATION)(request, membership_plan)


register_entity(
    EntityConfig(
        name="membership_plan",
        url_path="membership-plans",
        verbose_name="Membership Plan",
        model=MembershipPlan,
        form_class=MembershipPlanForm,
        datatable_view=MembershipPlanDataTableView,
        fields=[],
        tabs=[
            {
                "key": "basic",
                "label": "Basic",
                "fields": [
                    {
                        "name": "name",
                        "label": "Plan Name",
                        "type": "text",
                        "required": True,
                        "col": 6,
                        "placeholder": "Monthly Unlimited",
                    },
                    {
                        "name": "access_type",
                        "label": "Access Type",
                        "type": "select",
                        "required": True,
                        "col": 6,
                        "url_name": "access_type_select",
                    },
                    {
                        "name": "plan_type",
                        "label": "Plan Type",
                        "type": "static_select",
                        "required": True,
                        "col": 4,
                        "options": MembershipPlan.PLAN_TYPE_CHOICES,
                    },
                    {
                        "name": "duration_days",
                        "label": "Duration Days",
                        "type": "number",
                        "required": True,
                        "col": 4,
                        "min": 1,
                        "step": 1,
                    },
                    {
                        "name": "session_limit",
                        "label": "Session Limit",
                        "type": "number",
                        "required": False,
                        "col": 4,
                        "min": 0,
                        "step": 1,
                        "placeholder": "Leave blank for unlimited",
                    },
                    {
                        "name": "freeze_limit_days",
                        "label": "Freeze Limit Days",
                        "type": "number",
                        "required": True,
                        "col": 4,
                        "min": 0,
                        "step": 1,
                    },
                    {
                        "name": "branch",
                        "label": "Branch",
                        "type": "select",
                        "required": True,
                        "col": 4,
                        "url_name": "branch_select",
                    },
                    {
                        "name": "is_active",
                        "label": "Is Active",
                        "type": "checkbox",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "description",
                        "label": "Description",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                    },
                    {
                        "name": "remarks",
                        "label": "Remarks",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                    },
                ],
            },
            {
                "key": "restrictions",
                "label": "Restrictions",
                "requires_id": True,
                "fields": [],
                "sections": ["restrictions"],
            },
        ],
        dynamic_sections={"restrictions": RESTRICTION_SECTION},
        dynamic_sections_loader=_load_restrictions,
        dynamic_sections_saver=_save_restrictions,
        datatable_columns=[
            {
                "name": key,
                "title": "Active" if key == "is_active" else key.replace("_", " ").title(),
                **({"render": "function(data){return data ? 'Yes' : 'No';}"} if key == "is_active" else {}),
            }
            for key, _accessor in MEMBERSHIP_PLAN_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True, "freeze_limit_days": 0, "plan_type": "duration_based"},
        select_search_fields=["name", "access_type__name", "access_type__code", "description", "branch__name"],
        select_label_func=lambda obj: f"{obj.name} - {obj.access_type.name}",
    )
)
