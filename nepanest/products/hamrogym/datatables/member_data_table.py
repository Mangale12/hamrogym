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
    ("activity_level", lambda obj: obj.activity_level.name if obj.activity_level_id else ""),
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
        "status__name",
        "activity_level__name",
        "emergency_contact_name",
        "emergency_contact_phone",
        "remarks",
    ]
    orderable_columns = [
        "member_code",
        "party__name",
        "branch__name",
        "join_date",
        "status__name",
        "activity_level__name",
        "emergency_contact_name",
        "emergency_contact_phone",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("party", "branch", "profile", "status", "activity_level")
