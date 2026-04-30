from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.member_referral_data_table import MEMBER_REFERRAL_COLUMNS, MemberReferralDataTableView
from ...forms.member_referral_form import MemberReferralForm
from ...models import MemberReferral


register_entity(
    EntityConfig(
        name="member_referral",
        url_path="member-referrals",
        verbose_name="Member Referral",
        model=MemberReferral,
        form_class=MemberReferralForm,
        datatable_view=MemberReferralDataTableView,
        fields=[
            {
                "name": "referrer_member",
                "label": "Referrer Member",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "member_select",
            },
            {
                "name": "referred_member",
                "label": "Referred Member",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "member_select",
            },
            {
                "name": "referral_date",
                "label": "Referral Date",
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
                "name": "notes",
                "label": "Notes",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in MEMBER_REFERRAL_COLUMNS
            if key != "id"
        ],
        select_search_fields=[
            "referrer_member__member_code",
            "referrer_member__party__name",
            "referred_member__member_code",
            "referred_member__party__name",
        ],
        select_label_func=lambda obj: (
            f"{obj.referrer_member.member_code} -> {obj.referred_member.member_code}"
        ),
    )
)
