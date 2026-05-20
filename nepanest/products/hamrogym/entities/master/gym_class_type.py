from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.gym_class_type_data_table import GymClassTypeDataTableView, GYM_CLASS_COLUMNS
from ...forms.gym_class_type_form import GymClassTypeForm
from ...models import GymClassType


register_entity(
    EntityConfig(
        name="gym_class_type",
        url_path="gym-class-types",
        verbose_name="Gym Class Type",
        model=GymClassType,
        form_class=GymClassTypeForm,
        datatable_view=GymClassTypeDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in GYM_CLASS_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
