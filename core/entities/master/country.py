from core.config import EntityConfig
from core.datatables.country import CountryDataTableView
from core.forms import CountryForm
from nepanest.foundation.geography import Country
from core.registry import register_entity


register_entity(
    EntityConfig(
        name="country",
        url_path="countries",
        verbose_name="Country",
        model=Country,
        form_class=CountryForm,
        datatable_view=CountryDataTableView,
        fields=[
            {
                "name": "name",
                "label": "Country Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Nepal",
            },
            {
                "name": "iso2",
                "label": "ISO2",
                "type": "text",
                "required": False,
                "col": 3,
                "placeholder": "NP",
                "attributes": {"maxlength": "2"},
            },
            {
                "name": "iso3",
                "label": "ISO3",
                "type": "text",
                "required": False,
                "col": 3,
                "placeholder": "NPL",
                "attributes": {"maxlength": "3"},
            },
            {
                "name": "phone_code",
                "label": "Phone Code",
                "type": "text",
                "required": False,
                "col": 3,
                "placeholder": "+977",
            },
            {
                "name": "is_active",
                "label": "Active",
                "type": "checkbox",
                "required": False,
                "col": 3,
                "default": True,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
                "placeholder": "Optional notes",
            },
        ],
        datatable_columns=[
            {"name": "name", "title": "Name"},
            {"name": "iso2", "title": "ISO2"},
            {"name": "iso3", "title": "ISO3"},
            {"name": "phone_code", "title": "Phone Code"},
            {
                "name": "is_active",
                "title": "Active",
                "render": "function(data){return data ? 'Yes' : 'No';}",
            },
        ],
        reset_defaults={"is_active": True},
    )
)
