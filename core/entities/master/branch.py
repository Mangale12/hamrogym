from core.config import EntityConfig
from core.datatables.branch import BranchDataTableView
from core.forms.branch_form import BranchForm
from nepanest.foundation.organization import Branch
from core.registry import register_entity


register_entity(
    EntityConfig(
        name="branch",
        url_path="branches",
        verbose_name="Branch",
        model=Branch,
        form_class=BranchForm,
        datatable_view=BranchDataTableView,
        fields=[
            {
                "name": "organization",
                "label": "Organization",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "organization_select",
            },
            {
                "name": "name",
                "label": "Branch Name",
                "type": "text",
                "required": True,
                "col": 6,
                "placeholder": "Kathmandu",
            },
            {
                "name": "code",
                "label": "Code",
                "type": "text",
                "required": False,
                "col": 3,
                "placeholder": "KTM",
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
            {"name": "organization", "title": "Organization"},
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
