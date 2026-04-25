from core.config import EntityConfig
from core.registry import register_entity
from nepanest.modules.recruitment.datatables import SKILL_LEVEL_COLUMNS, SkillLevelDataTableView
from nepanest.modules.recruitment.forms import SkillLevelForm
from nepanest.modules.recruitment.models import SkillLevel


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
