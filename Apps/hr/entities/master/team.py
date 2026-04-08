from Apps.hr.models.team import TeamMember
from core.choices import TEAM_TYPE_CHOICES
from core.config import EntityConfig
from core.registry import register_entity

from Apps.hr.datatables.team_data_table import TEAM_COLUMNS, TeamDataTableView
from Apps.hr.forms import TeamForm
from Apps.hr.models import Team
from core.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

TEAM_MEMBERS_SECTION = {
    "title" : "Team Members",
    "layout" : "table",
    "allow_add": True,
    "fields" : [
        {"name": "user", "label": "User", "type": "select", "required": True, "url_name": "user_select"},
        {"name": "role", "label": "Role", "type": "select", "required": True, "url_name": "team_role_select"},
        {"name": "leader", "label": "Leader", "type": "checkbox", "required": False},
        {"name": "start_date", "label": "Start Date", "type": "date", "required": False},
        {"name": "end_date", "label": "End Date", "type": "date", "required": False},
    ]
}

TEAM_MEMBER_FIELD_NAMES = [
    "user",
    "role",
    "leader",
    "start_date",
    "end_date",
]

TEAM_MEMBERS_SECTION_RELATION = RelatedDynamicSectionConfig(
    section_name="team_members",
    related_model=TeamMember,
    parent_field="team",
    fields=TEAM_MEMBER_FIELD_NAMES,
    required_fields=["user", "role"],
    bool_fields=["leader"],
    empty_check_fields=TEAM_MEMBER_FIELD_NAMES,
)

_save_team_members = build_related_section_saver(TEAM_MEMBERS_SECTION_RELATION)
_load_team_members = build_related_section_loader(TEAM_MEMBERS_SECTION_RELATION)

_datatable_columns = []
for key, _accessor in TEAM_COLUMNS:
    if key == "id":
        continue
    column = {"name": key, "title": key.replace("_", " ").title()}
    if key == "is_active":
        column["title"] = "Active"
        column["render"] = "function(data){return data ? 'Yes' : 'No';}"
    _datatable_columns.append(column)


register_entity(
    EntityConfig(
        name="team",
        url_path="teams",
        verbose_name="Team",
        model=Team,
        form_class=TeamForm,
        datatable_view=TeamDataTableView,
        fields=[
            {
                "name": "organization",
                "label": "Organization",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "organization_select",
            },
            {
                "name": "branch",
                "label": "Branch",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "branch_select",
            },
            {
                "name": "department",
                "label": "Department",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "department_select",
            },
            {
                "name": "parent_team",
                "label": "Parent Team",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "team_select",
            },
            {
                "name": "name",
                "label": "Team Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Engineering",
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": False,
                "col": 3,
                "placeholder": "ENG",
            },
            {
                "name": "team_type",
                "label": "Team Type",
                "type": "static_select",
                "required": False,
                "col": 3,
                "options": TEAM_TYPE_CHOICES,
            },
            {
                "name": "leader",
                "label": "Leader",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "user_select",
            },
            {
                "name": "start_date",
                "label": "Start Date",
                "type": "date",
                "required": False,
                "col": 3,
            },
            {
                "name": "end_date",
                "label": "End Date",
                "type": "date",
                "required": False,
                "col": 3,
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
        dynamic_sections={
            "team_members": TEAM_MEMBERS_SECTION,
        },
        dynamic_sections_loader=_load_team_members,
        dynamic_sections_saver=_save_team_members,
        datatable_columns=_datatable_columns,
        reset_defaults={"is_active": True},
    )
)
