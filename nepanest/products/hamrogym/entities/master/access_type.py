from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.access_type_data_table import ACCESS_TYPE_COLUMNS, AccessTypeDataTableView
from ...forms.access_type_form import AccessTypeForm
from ...models import AccessType


register_entity(
    EntityConfig(
        name="access_type",
        url_path="access-types",
        verbose_name="Access Type",
        model=AccessType,
        form_class=AccessTypeForm,
        datatable_view=AccessTypeDataTableView,
        fields=[
            {
                "name": "name",
                "label": "Access Type Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Full Gym",
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "full_gym",
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
                "required": False,
                "col": 6,
            },
            {
                "name": "description",
                "label": "Description",
                "type": "textarea",
                "required": False,
                "col": 12,
                "placeholder": "Describe how this access type is used",
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
                "placeholder": "Optional internal notes",
            },
        ],
        datatable_columns=[
            {
                "name": key,
                "title": "Active" if key == "is_active" else key.replace("_", " ").title(),
                **({"render": "function(data){return data ? 'Yes' : 'No';}"} if key == "is_active" else {}),
            }
            for key, _accessor in ACCESS_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
        select_search_fields=["name", "code", "description", "branch__name", "remarks"],
        select_label_func=lambda obj: f"{obj.name} ({obj.code})",
    )
)
