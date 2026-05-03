from nepanest.common.helpers.helper import encode_datetime_for_display

from core.datatables.views import BaseDataTableView

from ..models import AccessViolation


ACCESS_VIOLATION_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: obj.member.member_code),
    ("member_name", lambda obj: obj.member.party.display_name or obj.member.party.name),
    ("membership", lambda obj: obj.membership.membership_plan.name if obj.membership_id else ""),
    ("violation_type", "violation_type"),
    ("detected_at", lambda obj, request: encode_datetime_for_display(obj.detected_at, request)),
    ("action_taken", "action_taken"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class AccessViolationDataTableView(BaseDataTableView):
    model = AccessViolation
    columns = ACCESS_VIOLATION_COLUMNS
    searchable_columns = [
        "member__member_code",
        "member__party__name",
        "member__party__display_name",
        "membership__membership_plan__name",
        "violation_type",
        "action_taken",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "member__member_code",
        "member__party__name",
        "membership__membership_plan__name",
        "violation_type",
        "detected_at",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("member__party", "membership__membership_plan", "branch")
