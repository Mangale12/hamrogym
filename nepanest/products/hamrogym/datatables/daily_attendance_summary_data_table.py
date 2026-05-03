from nepanest.common.helpers.helper import encode_date_for_display

from core.datatables.views import BaseDataTableView

from ..models import DailyAttendanceSummary


DAILY_ATTENDANCE_SUMMARY_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: obj.member.member_code),
    ("member_name", lambda obj: obj.member.party.display_name or obj.member.party.name),
    ("date", lambda obj, request: encode_date_for_display(obj.date, request)),
    ("total_checkins", "total_checkins"),
    ("total_duration", "total_duration"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class DailyAttendanceSummaryDataTableView(BaseDataTableView):
    model = DailyAttendanceSummary
    columns = DAILY_ATTENDANCE_SUMMARY_COLUMNS
    searchable_columns = [
        "member__member_code",
        "member__party__name",
        "member__party__display_name",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "member__member_code",
        "member__party__name",
        "date",
        "total_checkins",
        "total_duration",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("member__party", "branch")
