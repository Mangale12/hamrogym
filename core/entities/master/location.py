from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.location_data_table import LocationDataTableView, LOCATION_COLUMNS
from ...forms.location_form import LocationForm
from ...models import Location


register_entity(
    EntityConfig(
        name="location",
        url_path="locations",
        verbose_name="Location",
        model=Location,
        form_class=LocationForm,
        datatable_view=LocationDataTableView,
        fields=[
            {
                "name": "location_type",
                "label": "Location Type",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "location_type_select",
            },
            {
                "name": "name",
                "label": "Name",
                "type": "text",
                "required": True,
                "col": 6,
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": False,
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
            for key, _accessor in LOCATION_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
        select_search_fields=["name", "code", "location_type__name"],
        select_label_field="name",
    )
)
