from nepanest.common.helpers.helper import encode_date_for_display

from core.datatables.views import BaseDataTableView

from ..models import MemberReferral


MEMBER_REFERRAL_COLUMNS = [
    ("id", "id"),
    ("referrer_member", lambda obj: obj.referrer_member.member_code),
    ("referrer_name", lambda obj: obj.referrer_member.party.display_name or obj.referrer_member.party.name),
    ("referred_member", lambda obj: obj.referred_member.member_code),
    ("referred_name", lambda obj: obj.referred_member.party.display_name or obj.referred_member.party.name),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
    ("referral_date", lambda obj, request: encode_date_for_display(obj.referral_date, request)),
    ("notes", "notes"),
]


class MemberReferralDataTableView(BaseDataTableView):
    model = MemberReferral
    columns = MEMBER_REFERRAL_COLUMNS
    searchable_columns = [
        "referrer_member__member_code",
        "referrer_member__party__name",
        "referrer_member__party__display_name",
        "referred_member__member_code",
        "referred_member__party__name",
        "referred_member__party__display_name",
        "branch__name",
        "notes",
    ]
    orderable_columns = [
        "referrer_member__member_code",
        "referrer_member__party__name",
        "referred_member__member_code",
        "referred_member__party__name",
        "branch__name",
        "referral_date",
    ]

    def get_queryset(self):
        return self.model.objects.select_related(
            "referrer_member__party",
            "referred_member__party",
            "branch",
        )
