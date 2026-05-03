from core.datatables.views import BaseDataTableView

from ..models import MembershipExtension


MEMBERSHIP_EXTENSION_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: obj.membership.member.member_code),
    ("member_name", lambda obj: obj.membership.member.party.display_name or obj.membership.member.party.name),
    ("membership", lambda obj: obj.membership.membership_plan.name),
    ("extra_days", "extra_days"),
    ("reason", "reason"),
    ("approved_by", lambda obj: obj.approved_by.get_full_name() or obj.approved_by.username if obj.approved_by else ""),
]


class MembershipExtensionDataTableView(BaseDataTableView):
    model = MembershipExtension
    columns = MEMBERSHIP_EXTENSION_COLUMNS
    searchable_columns = [
        "membership__member__member_code",
        "membership__member__party__name",
        "membership__member__party__display_name",
        "membership__membership_plan__name",
        "extra_days",
        "reason",
        "approved_by__username",
        "approved_by__first_name",
        "approved_by__last_name",
    ]
    orderable_columns = [
        "membership__member__member_code",
        "membership__member__party__name",
        "membership__membership_plan__name",
        "extra_days",
        "reason",
        "approved_by__username",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("membership__member__party", "membership__membership_plan", "approved_by")
