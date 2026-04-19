from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.party_role_data_table import PARTY_ROLE_COLUMNS, PartyRoleDataTableView
from ...forms.party_role_form import PartyRoleForm
from ...models import PartyRole


register_entity(
    EntityConfig(
        name="party_role",
        url_path="party-roles",
        verbose_name="Party Role",
        model=PartyRole,
        form_class=PartyRoleForm,
        datatable_view=PartyRoleDataTableView,
        fields=[
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
                "required": True,
                "col": 6,
            },
            {
                "name": "is_active",
                "label": "Is Active",
                "type": "checkbox",
                "required": False,
                "col": 12,
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
            for key, _accessor in PARTY_ROLE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
        select_search_fields=["name", "code"],
        select_label_field="name",
    )
)
