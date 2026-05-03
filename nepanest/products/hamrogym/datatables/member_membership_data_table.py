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
    ("total_sessions", "total_sessions"),
    ("used_sessions", "used_sessions"),
    ("remaining_sessions", lambda obj: obj.remaining_sessions if obj.remaining_sessions is not None else ""),
    ("status", "status"),
    ("source", "source"),
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
        "source",
        "branch__name",
        "notes",
        "remarks",
    ]
    orderable_columns = [
        "member__member_code",
        "member__party__name",
        "membership_plan__name",
        "start_date",
        "end_date",
        "total_sessions",
        "used_sessions",
        "status",
        "source",
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
    ("total_days", "total_days"),
    ("reason", "reason"),
    ("approved_by", lambda obj: obj.approved_by.get_full_name() or obj.approved_by.username if obj.approved_by else ""),
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
        "approved_by__username",
        "approved_by__first_name",
        "approved_by__last_name",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "member__member_code",
        "member__party__name",
        "membership__membership_plan__name",
        "start_date",
        "end_date",
        "total_days",
        "reason",
        "approved_by__username",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("member__party", "membership__membership_plan", "approved_by", "branch")
