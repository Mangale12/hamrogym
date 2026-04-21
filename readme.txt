HOW TO CREATE NEW ENTITY CRUD
=============================

1. GENERATE COMMAND

Use this command:

```bash
python3 manage.py generate_entity <app_label> <entity_name> <ModelName> --group master
```

Example:

```bash
python3 manage.py generate_entity core  approval_workflow --group master --url-path approval-workflows --verbose-name="Approval Workflow" --create-model approval_workflow
```

If you also want model file scaffold:

```bash
python3 manage.py generate_entity hr project Project --group master --create-model
```

Optional arguments:

```bash
--url-path projects
--verbose-name "Project"
--force
```


2. WHAT THIS COMMAND CREATES

Example for:

```bash
python3 manage.py generate_entity hr project Project --group master --create-model
```

It creates:

1. `Nepanest/hr/entities/master/project.py`
2. `Nepanest/hr/datatables/project_data_table.py`
3. `Nepanest/hr/forms/project_form.py`
4. `Nepanest/hr/models/project.py` if `--create-model` is used

It also updates:

1. `Nepanest/hr/entities/__init__.py`
2. `Nepanest/hr/entities/master/__init__.py`
3. `Nepanest/hr/models/__init__.py` if model was generated inside `models/`


3. AFTER GENERATE, WHERE TO CHANGE

3.1 Model

File:

`Nepanest/hr/models/project.py`

Change here:

1. database fields
2. foreign keys
3. defaults
4. validation
5. mixins like fiscal year, organization, branch

Example:

```python
from django.db import models
from core.mixins import FiscalYearModelMixin


class Project(FiscalYearModelMixin, models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Then run migration:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```


3.2 Form

File:

`Nepanest/hr/forms/project_form.py`

Change here:

1. which fields should be editable
2. which fields should be hidden from user

Example:

```python
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "code", "is_active", "remarks"]
```

Note:

If `fiscal_year` is auto-filled from session, do not include it in form fields.


3.3 Datatable

File:

`Nepanest/hr/datatables/project_data_table.py`

Change here:

1. list columns
2. searchable columns
3. orderable columns

Example:

```python
PROJECT_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("is_active", "is_active"),
]
```


3.4 EntityConfig

File:

`Nepanest/hr/entities/master/project.py`

Change here:

1. modal fields
2. labels
3. input types
4. select URLs
5. tabs
6. dynamic sections
7. datatable column titles
8. reset defaults

Example:

```python
register_entity(
    EntityConfig(
        name="project",
        url_path="projects",
        verbose_name="Project",
        model=Project,
        form_class=ProjectForm,
        datatable_view=ProjectDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "name", "title": "Name"},
            {"name": "code", "title": "Code"},
            {"name": "is_active", "title": "Active"},
        ],
        reset_defaults={"is_active": True},
    )
)
```


4. IF MODEL IS NOT AUTO-IMPORTED

If needed, check:

`Nepanest/hr/models/__init__.py`

Add:

```python
from .project import Project
```


5. IF ENTITY IS NOT AUTO-IMPORTED

Check:

1. `Nepanest/hr/entities/__init__.py`
2. `Nepanest/hr/entities/master/__init__.py`

Make sure generated import exists.


6. SIDEBAR

If you want it in sidebar, add it in app sidebar file.

Example:

`Nepanest/hr/sidebar.py`

Add item like:

```python
{
    "label": "Project",
    "icon": "fas fa-folder",
    "url_name": "project_list",
}
```


7. URLS AND VIEWS

This project uses generic entity views.

Usually you need a view wrapper file like:

`Nepanest/hr/views/project.py`

Pattern:

```python
from core.views.entities import build_entity_views
from core.registry import get_entity_config

_entity = get_entity_config("project")
_views = build_entity_views(_entity)

ProjectListView = _views["list_view"]
ProjectDetailView = _views["detail_view"]
ProjectCreateView = _views["create_view"]
ProjectUpdateView = _views["update_view"]
ProjectDeleteView = _views["delete_view"]
ProjectDataTableView = _views["datatable_view"]
ProjectSelectView = _views["select_view"]
```

Then include URLs in your app or project url config.

Check existing pattern in:

1. `core/views/fiscal_year.py`
2. `core/urls.py`
3. `config/urls.py`


8. COMPLETE CHECKLIST

For a new entity, check these files:

1. `Nepanest/<app>/models/<entity>.py`
2. `Nepanest/<app>/models/__init__.py`
3. `Nepanest/<app>/forms/<entity>_form.py`
4. `Nepanest/<app>/datatables/<entity>_data_table.py`
5. `Nepanest/<app>/entities/master/<entity>.py`
6. `Nepanest/<app>/entities/master/__init__.py`
7. `Nepanest/<app>/views/<entity>.py`
8. `Nepanest/<app>/sidebar.py`
9. app urls or `config/urls.py`


9. SHORT PROCESS

1. Run generate command
2. Edit model
3. Run migrations
4. Edit form
5. Edit datatable
6. Edit entity config
7. Add view wrapper
8. Add URL
9. Add sidebar menu


10. QUICK EXAMPLE

```bash
python3 manage.py generate_entity hr project Project --group master --create-model
```

Then edit:

1. `Nepanest/hr/models/project.py`
2. `Nepanest/hr/forms/project_form.py`
3. `Nepanest/hr/datatables/project_data_table.py`
4. `Nepanest/hr/entities/master/project.py`
5. `Nepanest/hr/views/project.py`
6. `Nepanest/hr/sidebar.py`

Then run:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
