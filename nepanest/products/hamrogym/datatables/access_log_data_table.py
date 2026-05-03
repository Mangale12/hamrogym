from nepanest.common.helpers.helper import encode_datetime_for_display

from core.datatables.views import BaseDataTableView

from ..models import AccessLog


ACCESS_LOG_COLUMNS = [
    ("id", "id"),
    ("device", lambda obj: obj.device.name),
    ("member", lambda obj: obj.member.member_code if obj.member_id else ""),
    ("member_name", lambda obj: (obj.member.party.display_name or obj.member.party.name) if obj.member_id else ""),
    ("scan_time", lambda obj, request: encode_datetime_for_display(obj.scan_time, request)),
    ("raw_data", "raw_data"),
    ("processed", "processed"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class AccessLogDataTableView(BaseDataTableView):
    model = AccessLog
    columns = ACCESS_LOG_COLUMNS
    searchable_columns = [
        "device__name",
        "member__member_code",
        "member__party__name",
        "member__party__display_name",
        "raw_data",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "device__name",
        "member__member_code",
        "member__party__name",
        "scan_time",
        "processed",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("device", "member__party", "branch")
