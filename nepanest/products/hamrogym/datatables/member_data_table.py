from nepanest.common.helpers.helper import encode_date_for_display

from core.datatables.views import BaseDataTableView

from ..models import Member


MEMBER_COLUMNS = [
    ("id", "id"),
    ("member_code", "member_code"),
    ("party", lambda obj: obj.party.display_name or obj.party.name),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
    ("join_date", lambda obj, request: encode_date_for_display(obj.join_date, request)),
    ("status", lambda obj: obj.get_status_display()),
    ("emergency_contact_name", "emergency_contact_name"),
    ("emergency_contact_phone", "emergency_contact_phone"),
]


class MemberDataTableView(BaseDataTableView):
    model = Member
    columns = MEMBER_COLUMNS
    searchable_columns = [
        "member_code",
        "party__name",
        "party__display_name",
        "branch__name",
        "status",
        "emergency_contact_name",
        "emergency_contact_phone",
        "remarks",
    ]
    orderable_columns = [
        "member_code",
        "party__name",
        "branch__name",
        "join_date",
        "status",
        "emergency_contact_name",
        "emergency_contact_phone",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("party", "branch", "profile")
