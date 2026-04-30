from core.datatables.views import BaseDataTableView

from ..models import MembershipPlan


MEMBERSHIP_PLAN_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("duration_days", "duration_days"),
    ("session_limit", "session_limit"),
    ("access_type", "access_type.name"),
    ("freeze_limit_days", "freeze_limit_days"),
    ("branch", "branch.name"),
    ("is_active", "is_active"),
]


class MembershipPlanDataTableView(BaseDataTableView):
    model = MembershipPlan
    columns = MEMBERSHIP_PLAN_COLUMNS
    searchable_columns = [
        "name",
        "access_type__name",
        "access_type__code",
        "description",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "duration_days",
        "session_limit",
        "access_type__name",
        "freeze_limit_days",
        "branch__name",
        "is_active",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("access_type", "branch")
