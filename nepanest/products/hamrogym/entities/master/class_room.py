from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.class_room_data_table import ClassRoomDataTableView, CLASS_ROOM_COLUMNS
from ...forms.class_room_form import ClassRoomForm
from ...models import ClassRoom


register_entity(
    EntityConfig(
        name="class_room",
        url_path="class-rooms",
        verbose_name="Class Room",
        model=ClassRoom,
        form_class=ClassRoomForm,
        datatable_view=ClassRoomDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "capacity", "label": "Capacity", "type": "number", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in CLASS_ROOM_COLUMNS
            if key != "id" 
        ],
        reset_defaults={},
    )
)
