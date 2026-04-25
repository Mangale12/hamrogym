from core.config import EntityConfig
from core.datatables.state import StateDataTableView
from core.forms import StateForm
from nepanest.foundation.geography import State
from core.registry import register_entity


register_entity(
    EntityConfig(
        name="state",
        url_path="states",
        verbose_name="State",
        model=State,
        form_class=StateForm,
        datatable_view=StateDataTableView,
        fields=[
            {
                "name": "country",
                "label": "Country",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "country_select",
            },
            {
                "name": "name",
                "label": "State Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Bagmati",
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": False,
                "col": 3,
                "placeholder": "BG",
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
            {"name": "country", "title": "Country"},
            {"name": "code", "title": "Code"},
            {
                "name": "is_active",
                "title": "Active",
                "render": "function(data){return data ? 'Yes' : 'No';}",
            },
        ],
        reset_defaults={"is_active": True},
        select_search_fields=["name", "code", "country__name"],
        select_label_field="name",
    )
)
