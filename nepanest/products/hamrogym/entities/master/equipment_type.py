from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.equipment_type_data_table import EquipmentTypeDataTableView, EQUIPMENT_TYPE_COLUMNS
from ...forms.equipment_type_form import EquipmentTypeForm
from ...models import EquipmentType


register_entity(
    EntityConfig(
        name="equipment_type",
        url_path="equipment-types",
        verbose_name="Equipment Type",
        model=EquipmentType,
        form_class=EquipmentTypeForm,
        datatable_view=EquipmentTypeDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "boolean", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in EQUIPMENT_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
