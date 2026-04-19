from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.party_type_data_table import PARTY_TYPE_COLUMNS, PartyTypeDataTableView
from ...forms.party_type_form import PartyTypeForm
from ...models import PartyType


register_entity(
    EntityConfig(
        name="party_type",
        url_path="party-types",
        verbose_name="Party Type",
        model=PartyType,
        form_class=PartyTypeForm,
        datatable_view=PartyTypeDataTableView,
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
            for key, _accessor in PARTY_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
        select_search_fields=["name"],
        select_label_field="name",
    )
)
