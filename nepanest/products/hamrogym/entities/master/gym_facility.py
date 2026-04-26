from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.gym_facility_data_table import GymFacilityDataTableView, GYM_FACILITY_COLUMNS
from ...forms.gym_facility_form import GymFacilityForm
from ...models import GymFacility


register_entity(
    EntityConfig(
        name="gym_facility",
        url_path="gym-facilities",
        verbose_name="Gym Facility",
        model=GymFacility,
        form_class=GymFacilityForm,
        datatable_view=GymFacilityDataTableView,
        fields=[
            {
                "name": "name",
                "label": "Facility Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Cardio Zone",
            },
            {
                "name": "branch",
                "label": "Branch",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "branch_select",
            },
            {
                "name": "is_active",
                "label": "Is Active",
                "type": "checkbox",
                "required": True,
                "col": 6,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
                "placeholder": "Optional facility details",
            },
        ],
        datatable_columns=[
            {
                "name": key,
                "title": "Active" if key == "is_active" else key.replace("_", " ").title(),
                **({"render": "function(data){return data ? 'Yes' : 'No';}"} if key == "is_active" else {}),
            }
            for key, _accessor in GYM_FACILITY_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
        select_search_fields=["name", "branch__name", "remarks"],
    )
)
