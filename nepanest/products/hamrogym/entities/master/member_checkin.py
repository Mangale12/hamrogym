from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.member_checkin_data_table import MEMBER_CHECKIN_COLUMNS, MemberCheckinDataTableView
from ...forms.member_checkin_form import MemberCheckinForm
from ...models import MemberCheckin


register_entity(
    EntityConfig(
        name="member_checkin",
        url_path="member-checkins",
        verbose_name="Member Checkin",
        model=MemberCheckin,
        form_class=MemberCheckinForm,
        datatable_view=MemberCheckinDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 6, "url_name": "member_select"},
            {
                "name": "member_membership",
                "label": "Membership",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "member_membership_select",
            },
            {"name": "checkin_time", "label": "Check-in Time", "type": "datetime-local", "required": True, "col": 4},
            {
                "name": "checkin_type",
                "label": "Check-in Type",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": [("", "Select Type"), *MemberCheckin.CheckinType.choices],
            },
            {"name": "checkout_time", "label": "Checkout Time", "type": "datetime-local", "required": False, "col": 4},
            {
                "name": "source",
                "label": "Source",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": [("", "Select Source"), *MemberCheckin.Source.choices],
            },
            {"name": "device", "label": "Device", "type": "select", "required": False, "col": 4, "url_name": "access_device_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "is_valid", "label": "Is Valid", "type": "checkbox", "required": False, "col": 4},
            {"name": "rejection_reason", "label": "Rejection Reason", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {
                "name": key,
                "title": "Valid" if key == "is_valid" else key.replace("_", " ").title(),
                **({"render": "function(data){return data ? 'Yes' : 'No';}"} if key == "is_valid" else {}),
            }
            for key, _accessor in MEMBER_CHECKIN_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "checkin_type": MemberCheckin.CheckinType.GYM,
            "source": MemberCheckin.Source.MANUAL,
            "is_valid": True,
        },
        select_search_fields=[
            "member__member_code",
            "member__party__name",
            "member_membership__membership_plan__name",
            "device__name",
        ],
        select_label_func=lambda obj: (
            f"{obj.member.member_code} - {obj.member_membership.membership_plan.name} "
            f"({obj.checkin_time:%Y-%m-%d %H:%M})"
        ),
    )
)
