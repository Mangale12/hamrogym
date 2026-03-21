from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_skill_data_table import JobSkillDataTableView, JOB_SKILL_COLUMNS
from ...forms.job_skill_form import JobSkillForm
from ...models import JobSkill


register_entity(
    EntityConfig(
        name="job_skill",
        url_path="job-skills",
        verbose_name="Job Skill",
        model=JobSkill,
        form_class=JobSkillForm,
        datatable_view=JobSkillDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_SKILL_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
