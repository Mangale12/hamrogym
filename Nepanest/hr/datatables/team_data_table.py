from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display

from Nepanest.hr.models import Team


TEAM_COLUMNS = [
    ("id", "id"),
    ("organization", "organization.name"),
    ("branch", "branch.name"),
    ("department", "department.name"),
    ("parent_team", "parent_team.name"),
    ("name", "name"),
    ("code", "code"),
    ("team_type", "team_type"),
    ("leader", lambda obj: (obj.leader.get_full_name() or obj.leader.username) if obj.leader_id else ""),
    ("start_date", lambda obj, request: encode_date_for_display(obj.start_date, request)),
    ("end_date", lambda obj, request: encode_date_for_display(obj.end_date, request)),
    ("is_active", "is_active"),
]


class TeamDataTableView(BaseDataTableView):
    model = Team
    columns = TEAM_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "department__name",
        "parent_team__name",
        "organization__name",
        "branch__name",
        "team_type",
        "leader__username",
        "leader__first_name",
        "leader__last_name",
    ]
    orderable_columns = [
        "organization__name",
        "branch__name",
        "department__name",
        "parent_team__name",
        "name",
        "code",
        "team_type",
        "leader__username",
        "start_date",
        "end_date",
        "is_active",
    ]
