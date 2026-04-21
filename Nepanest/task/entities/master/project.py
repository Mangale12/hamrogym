from core.choices import PRIORITY_CHOICES
from Nepanest.task.models.project import ProjectRole, ProjectStatus
from core.config import EntityConfig
from core.registry import register_entity
from core.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)
from ...datatables.project_data_table import ProjectDataTableView, PROJECT_COLUMNS
from ...forms.project_form import ProjectForm
from ...models import Project, ProjectMember, ProjectEpic


PROJECT_MEMBER_SECTION = {
    "title": "Project Members",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "user", "label": "User", "type": "select", "required": True, "url_name": "user_select"},
        {"name": "role", "label": "Role", "type": "static_select", "required": True, "options": ProjectRole.choices},
    ],
}


PROJECT_EPIC_SECTION = {
    "title": "Project Epics",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "name", "label": "Name", "type": "text", "required": True},
        {"name": "description", "label": "Description", "type": "textarea", "required": False},
        {"name": "status", "label": "Status", "type": "static_select", "required": True, "options": ProjectStatus.choices},
        {"name": "start_date", "label": "Start Date", "type": "date", "required": False},
        {"name": "end_date", "label": "End Date", "type": "date", "required": False},
        {"name": "priority", "label": "Priority", "type": "static_select", "required": True, "options": PRIORITY_CHOICES},
        {"name": "progress", "label": "Progress", "type": "number", "required": False, "min": 0},
    ],
}


PROJECT_MEMBER_FIELDS = ["user", "role"]
PROJECT_EPIC_FIELDS = ["name", "description", "status", "start_date", "end_date", "priority", "progress"]

PROJECT_MEMBER_RELATION = RelatedDynamicSectionConfig(
    section_name="project_members",
    related_model=ProjectMember,
    parent_field="project",
    fields=PROJECT_MEMBER_FIELDS,
    required_fields=["user", "role"],
    bool_fields=[],
    empty_check_fields=PROJECT_MEMBER_FIELDS,
    save_transformers={
        "user": lambda value: (value or "").strip(),
        "role": lambda value: (value or "").strip(),
    },
)

PROJECT_EPIC_RELATION = RelatedDynamicSectionConfig(
    section_name="project_epics",
    related_model=ProjectEpic,
    parent_field="project",
    fields=PROJECT_EPIC_FIELDS,
    required_fields=["name", "status", "priority"],
    bool_fields=[],
    empty_check_fields=PROJECT_EPIC_FIELDS,
    save_transformers={
        "name": lambda value: (value or "").strip(),
        "description": lambda value: (value or "").strip(),
        "status": lambda value: (value or "").strip(),
        "priority": lambda value: (value or "").strip(),
        "progress": lambda value: int(value) if str(value).strip() else 0,
    },
)

_save_project_member = build_related_section_saver(PROJECT_MEMBER_RELATION)
_save_project_epic = build_related_section_saver(PROJECT_EPIC_RELATION)
_load_project_member = build_related_section_loader(PROJECT_MEMBER_RELATION)
_load_project_epic = build_related_section_loader(PROJECT_EPIC_RELATION)


def _save_project_relations(request, project: Project) -> None:
    _save_project_member(request, project)
    _save_project_epic(request, project)


def _load_project_relations(project: Project):
    data = {}
    data.update(_load_project_member(project))
    data.update(_load_project_epic(project))
    return data


register_entity(
    EntityConfig(
        name="project",
        url_path="projects",
        verbose_name="Projects",
        model=Project,
        form_class=ProjectForm,
        datatable_view=ProjectDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "module", "label": "Module", "type": "select", "required": False, "col": 6, "url_name": "task_module_select"},
            {"name": "manager", "label": "Manager", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "options": ProjectStatus.choices, "col": 6},
            {"name": "priority", "label": "Priority", "type": "static_select", "required": True, "options": PRIORITY_CHOICES, "col": 6},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": False, "col": 6},
            {"name": "end_date", "label": "End Date", "type": "date", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        dynamic_sections={
            "project_members": PROJECT_MEMBER_SECTION,
            "project_epics": PROJECT_EPIC_SECTION,
        },
        dynamic_sections_loader=_load_project_relations,
        dynamic_sections_saver=_save_project_relations,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in PROJECT_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "status": ProjectStatus.PLANNED,
            "priority": "medium",
            "is_active": True,
        },
        select_search_fields=["name", "code", "module__name", "manager__username", "description"],
    )
)





