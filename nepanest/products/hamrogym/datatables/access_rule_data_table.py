from core.datatables.views import BaseDataTableView

from ..models import AccessRule


ACCESS_RULE_COLUMNS = [
    ("id", "id"),
    ("membership_plan", lambda obj: obj.membership_plan.name),
    ("rule_type", "rule_type"),
    ("time_range_start", lambda obj: obj.time_range_start.strftime("%H:%M:%S") if obj.time_range_start else ""),
    ("time_range_end", lambda obj: obj.time_range_end.strftime("%H:%M:%S") if obj.time_range_end else ""),
    ("allowed_days", "allowed_days"),
    ("max_checkins_per_day", "max_checkins_per_day"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
    ("is_active", "is_active"),
]


class AccessRuleDataTableView(BaseDataTableView):
    model = AccessRule
    columns = ACCESS_RULE_COLUMNS
    searchable_columns = [
        "membership_plan__name",
        "rule_type",
        "allowed_days",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "membership_plan__name",
        "rule_type",
        "time_range_start",
        "time_range_end",
        "max_checkins_per_day",
        "branch__name",
        "is_active",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("membership_plan", "branch")
