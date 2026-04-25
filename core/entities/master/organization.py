from core.config import EntityConfig
from core.datatables.organization import OrganizationDataTableView
from core.forms.organization_form import OrganizationForm
from nepanest.foundation.organization import Organization
from core.registry import register_entity


register_entity(
    EntityConfig(
        name="organization",
        url_path="organizations",
        verbose_name="Organization",
        model=Organization,
        form_class=OrganizationForm,
        datatable_view=OrganizationDataTableView,
        fields=[
            {
                "name": "name",
                "label": "Organization Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Hamro Group",
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": False,
                "col": 3,
                "placeholder": "HG",
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
            {"name": "code", "title": "Code"},
            {
                "name": "is_active",
                "title": "Active",
                "render": "function(data){return data ? 'Yes' : 'No';}",
            },
        ],
        reset_defaults={"is_active": True},
    )
)
