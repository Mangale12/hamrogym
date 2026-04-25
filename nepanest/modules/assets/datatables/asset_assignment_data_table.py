from django.utils.timezone import localdate

from core.datatables.views import BaseDataTableView

from ..models import AssetAssignment


ASSET_ASSIGNMENT_COLUMNS = [
    ("id", "id"),
    ("asset", "asset.name"),
    ("employee", "employee.full_name"),
    ("assigned_date", "assigned_date"),
    ("expected_return_date", "expected_return_date"),
    ("return_date", "return_date"),
    ("assigned_by", lambda obj: obj.assigned_by.get_full_name() or obj.assigned_by.username if obj.assigned_by else ""),
    ("received_by", lambda obj: obj.received_by.get_full_name() or obj.received_by.username if obj.received_by else ""),
    ("condition_at_issue", "condition_at_issue.name"),
    ("condition_at_return", "condition_at_return.name"),
    ("status", "status"),
    ("remarks", "remarks"),
]


class AssetAssignmentDataTableView(BaseDataTableView):
    model = AssetAssignment
    columns = ASSET_ASSIGNMENT_COLUMNS
    searchable_columns = [
        "asset__name",
        "asset__code",
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "employee__user__username",
        "assigned_by__first_name",
        "assigned_by__last_name",
        "assigned_by__username",
        "received_by__first_name",
        "received_by__last_name",
        "received_by__username",
        "condition_at_issue__name",
        "condition_at_return__name",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "asset__name",
        "employee__user__first_name",
        "assigned_date",
        "expected_return_date",
        "return_date",
        "assigned_by__username",
        "received_by__username",
        "condition_at_issue__name",
        "condition_at_return__name",
        "status",
        "remarks",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        overdue_only = (self.request.GET.get("overdue_only") or "").strip().lower()
        if overdue_only in {"1", "true", "yes", "on"}:
            today = localdate()
            queryset = queryset.filter(
                status=AssetAssignment.STATUS_ACTIVE,
                expected_return_date__isnull=False,
                expected_return_date__lt=today,
            )
        return queryset

    def serialize_row(self, obj):
        row = super().serialize_row(obj)
        row["is_overdue"] = bool(
            obj.status == AssetAssignment.STATUS_ACTIVE
            and obj.expected_return_date
            and obj.expected_return_date < localdate()
        )
        return row
