from core.datatables.views import BaseDataTableView

from nepanest.modules.people.models import TeamRole


TEAM_ROLE_COLUMNS = [
    ("id", "id"),
    ("organization", "organization.name"),
    ("branch", "branch.name"),
    ("name", "name"),
    ("code", "code"),
    ("level", "level"),
    ("is_active", "is_active"),
]


class TeamRoleDataTableView(BaseDataTableView):
    model = TeamRole
    columns = TEAM_ROLE_COLUMNS
    searchable_columns = ["name", "code", "organization__name", "branch__name"]
    orderable_columns = ["organization__name", "branch__name", "name", "code", "level", "is_active"]
