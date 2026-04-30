from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.member_membership_data_table import (
    MEMBER_MEMBERSHIP_COLUMNS,
    MEMBERSHIP_FREEZE_COLUMNS,
    MemberMembershipDataTableView,
    MembershipFreezeDataTableView,
)
from ...forms.member_membership_form import MemberMembershipForm, MembershipFreezeForm
from ...models import MemberMembership, MembershipFreeze


register_entity(
    EntityConfig(
        name="member_membership",
        url_path="member-memberships",
        verbose_name="Member Membership",
        model=MemberMembership,
        form_class=MemberMembershipForm,
        datatable_view=MemberMembershipDataTableView,
        fields=[
            {
                "name": "member",
                "label": "Member",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "member_select",
            },
            {
                "name": "membership_plan",
                "label": "Membership Plan",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "membership_plan_select",
            },
            {
                "name": "start_date",
                "label": "Start Date",
                "type": "date",
                "required": True,
                "col": 4,
                "calendar_switchable": False,
                "calendar_mode": "ad",
            },
            {
                "name": "end_date",
                "label": "End Date",
                "type": "date",
                "required": True,
                "col": 4,
                "calendar_switchable": False,
                "calendar_mode": "ad",
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": [("", "Select Status"), *MemberMembership.Status.choices],
            },
            {
                "name": "allowed_sessions",
                "label": "Allowed Sessions",
                "type": "number",
                "required": False,
                "col": 4,
                "min": 0,
                "step": 1,
            },
            {
                "name": "used_sessions",
                "label": "Used Sessions",
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
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in MEMBER_MEMBERSHIP_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": MemberMembership.Status.ACTIVE, "used_sessions": 0},
        select_search_fields=["member__member_code", "member__party__name", "membership_plan__name", "status"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.membership_plan.name}",
    )
)


register_entity(
    EntityConfig(
        name="membership_freeze",
        url_path="membership-freezes",
        verbose_name="Membership Freeze",
        model=MembershipFreeze,
        form_class=MembershipFreezeForm,
        datatable_view=MembershipFreezeDataTableView,
        fields=[
            {
                "name": "member",
                "label": "Member",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "member_select",
            },
            {
                "name": "membership",
                "label": "Membership",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "member_membership_select",
            },
            {
                "name": "start_date",
                "label": "Start Date",
                "type": "date",
                "required": True,
                "col": 4,
                "calendar_switchable": False,
                "calendar_mode": "ad",
            },
            {
                "name": "end_date",
                "label": "End Date",
                "type": "date",
                "required": True,
                "col": 4,
                "calendar_switchable": False,
                "calendar_mode": "ad",
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
                "name": "reason",
                "label": "Reason",
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
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in MEMBERSHIP_FREEZE_COLUMNS
            if key != "id"
        ],
        select_search_fields=["member__member_code", "member__party__name", "membership__membership_plan__name", "reason"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.membership.membership_plan.name}",
    )
)
