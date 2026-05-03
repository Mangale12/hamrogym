from nepanest.common.helpers.helper import encode_datetime_for_display

from core.datatables.views import BaseDataTableView

from ..models import MemberCheckin


MEMBER_CHECKIN_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: obj.member.member_code),
    ("member_name", lambda obj: obj.member.party.display_name or obj.member.party.name),
    ("membership_plan", lambda obj: obj.member_membership.membership_plan.name),
    ("checkin_time", lambda obj, request: encode_datetime_for_display(obj.checkin_time, request)),
    ("checkin_type", "checkin_type"),
    ("checkout_time", lambda obj, request: encode_datetime_for_display(obj.checkout_time, request) if obj.checkout_time else ""),
    ("source", "source"),
    ("device", lambda obj: obj.device.name if obj.device_id else ""),
    ("is_valid", "is_valid"),
    ("rejection_reason", "rejection_reason"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class MemberCheckinDataTableView(BaseDataTableView):
    model = MemberCheckin
    columns = MEMBER_CHECKIN_COLUMNS
    searchable_columns = [
        "member__member_code",
        "member__party__name",
        "member__party__display_name",
        "member_membership__membership_plan__name",
        "checkin_type",
        "source",
        "device__name",
        "rejection_reason",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "member__member_code",
        "member__party__name",
        "member_membership__membership_plan__name",
        "checkin_time",
        "checkin_type",
        "checkout_time",
        "source",
        "device__name",
        "is_valid",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related(
            "member__party", "member_membership__membership_plan", "device", "branch"
        )
