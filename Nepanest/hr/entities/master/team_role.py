from core.config import EntityConfig
from core.registry import register_entity

from Nepanest.hr.datatables.team_role_data_table import TEAM_ROLE_COLUMNS, TeamRoleDataTableView
from Nepanest.hr.forms import TeamRoleForm
from Nepanest.hr.models import TeamRole


_datatable_columns = []
for key, _accessor in TEAM_ROLE_COLUMNS:
    if key == "id":
        continue
    column = {"name": key, "title": key.replace("_", " ").title()}
    if key == "is_active":
        column["title"] = "Active"
        column["render"] = "function(data){return data ? 'Yes' : 'No';}"
    _datatable_columns.append(column)


register_entity(
    EntityConfig(
        name="team_role",
        url_path="team-roles",
        verbose_name="Team Role",
        model=TeamRole,
        form_class=TeamRoleForm,
        datatable_view=TeamRoleDataTableView,
        fields=[
            {
                "name": "name",
                "label": "Role Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Team Lead",
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": False,
                "col": 3,
                "placeholder": "TL",
            },
            {
                "name": "level",
                "label": "Level",
                "type": "number",
                "required": False,
                "col": 3,
                "placeholder": "1",
                "attributes": {"min": "1"},
            },
            {
                "name": "is_active",
                "label": "Active",
                "type": "checkbox",
                "required": False,
                "col": 3,
                "default": True,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
                "placeholder": "Optional notes",
            },
        ],
        datatable_columns=_datatable_columns,
        reset_defaults={"is_active": True, "level": 1},
    )
)
