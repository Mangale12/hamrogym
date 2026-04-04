from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.location_type_data_table import LocationTypeDataTableView, LOCATION_TYPE_COLUMNS
from ...forms.location_type_form import LocationTypeForm
from ...models import LocationType


register_entity(
    EntityConfig(
        name="location_type",
        url_path="location-types",
        verbose_name="Location Type",
        model=LocationType,
        form_class=LocationTypeForm,
        datatable_view=LocationTypeDataTableView,
        fields=[
            {
                "name": "name",
                "label": "Name",
                "type": "text",
                "required": True,
                "col": 6,
            },
            {
                "name": "is_active",
                "label": "Is Active",
                "type": "checkbox",
                "required": False,
                "col": 6,
                "default": True,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LOCATION_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
        select_search_fields=["name"],
        select_label_field="name",
    )
)
