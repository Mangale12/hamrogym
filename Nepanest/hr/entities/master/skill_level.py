from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.skill_level_data_table import SkillLevelDataTableView, SKILL_LEVEL_COLUMNS
from ...forms.skill_level_form import SkillLevelForm
from ...models import SkillLevel


register_entity(
    EntityConfig(
        name="skill_level",
        url_path="skill-levels",
        verbose_name="Skill Level",
        model=SkillLevel,
        form_class=SkillLevelForm,
        datatable_view=SkillLevelDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in SKILL_LEVEL_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
