from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.project_epic_data_table import PROJECT_EPIC_COLUMNS, ProjectEpicDataTableView
from ...forms.project_epic_form import ProjectEpicForm
from ...models import ProjectEpic


register_entity(
    EntityConfig(
        name="project_epic",
        url_path="project-epics",
        verbose_name="Project Epic",
        model=ProjectEpic,
        form_class=ProjectEpicForm,
        datatable_view=ProjectEpicDataTableView,
        fields=[
            {"name": "project", "label": "Project", "type": "select", "required": True, "col": 6, "url_name": "project_select"},
            {"name": "name", "label": "Epic Name", "type": "text", "required": True, "col": 6},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 4, "options": ProjectEpic._meta.get_field("status").choices},
            {"name": "priority", "label": "Priority", "type": "static_select", "required": True, "col": 4, "options": ProjectEpic._meta.get_field("priority").choices},
            {"name": "progress", "label": "Progress", "type": "number", "required": False, "col": 4, "min": 0, "max": 100},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": False, "col": 6},
            {"name": "end_date", "label": "End Date", "type": "date", "required": False, "col": 6},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in PROJECT_EPIC_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "status": "planned",
            "priority": "medium",
            "is_active": True,
        },
        select_search_fields=["name", "project__name", "status", "description"],
        select_label_func=lambda obj: f"{obj.project.name} - {obj.name}" if obj.project_id else obj.name,
        show_create=False,
    )
)
