from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.activity_level_data_table import ActivityLevelDataTableView, ACTIVITY_LEVEL_COLUMNS
from ...forms.activity_level_form import ActivityLevelForm
from ...models import ActivityLevel


register_entity(
    EntityConfig(
        name="activity_level",
        url_path="activity-levels",
        verbose_name="Activity Level",
        model=ActivityLevel,
        form_class=ActivityLevelForm,
        datatable_view=ActivityLevelDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ACTIVITY_LEVEL_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
