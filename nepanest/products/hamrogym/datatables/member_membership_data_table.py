from nepanest.common.helpers.helper import encode_date_for_display

from core.datatables.views import BaseDataTableView

from ..models import MemberMembership, MembershipFreeze


MEMBER_MEMBERSHIP_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: obj.member.member_code),
    ("member_name", lambda obj: obj.member.party.display_name or obj.member.party.name),
    ("membership_plan", lambda obj: obj.membership_plan.name),
    ("start_date", lambda obj, request: encode_date_for_display(obj.start_date, request)),
    ("end_date", lambda obj, request: encode_date_for_display(obj.end_date, request)),
    ("allowed_sessions", "allowed_sessions"),
    ("used_sessions", "used_sessions"),
    ("status", "status"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class MemberMembershipDataTableView(BaseDataTableView):
    model = MemberMembership
    columns = MEMBER_MEMBERSHIP_COLUMNS
    searchable_columns = [
        "member__member_code",
        "member__party__name",
        "member__party__display_name",
        "membership_plan__name",
        "status",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "member__member_code",
        "member__party__name",
        "membership_plan__name",
        "start_date",
        "end_date",
        "allowed_sessions",
        "used_sessions",
        "status",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("member__party", "membership_plan", "branch")


MEMBERSHIP_FREEZE_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: obj.member.member_code),
    ("member_name", lambda obj: obj.member.party.display_name or obj.member.party.name),
    ("membership", lambda obj: obj.membership.membership_plan.name),
    ("start_date", lambda obj, request: encode_date_for_display(obj.start_date, request)),
    ("end_date", lambda obj, request: encode_date_for_display(obj.end_date, request)),
    ("reason", "reason"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class MembershipFreezeDataTableView(BaseDataTableView):
    model = MembershipFreeze
    columns = MEMBERSHIP_FREEZE_COLUMNS
    searchable_columns = [
        "member__member_code",
        "member__party__name",
        "member__party__display_name",
        "membership__membership_plan__name",
        "reason",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "member__member_code",
        "member__party__name",
        "membership__membership_plan__name",
        "start_date",
        "end_date",
        "reason",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("member__party", "membership__membership_plan", "branch")
