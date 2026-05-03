from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.membership_extension_data_table import MembershipExtensionDataTableView, MEMBERSHIP_EXTENSION_COLUMNS
from ...forms.membership_extension_form import MembershipExtensionForm
from ...models import MembershipExtension


register_entity(
    EntityConfig(
        name="membership_extension",
        url_path="membership-extension",
        verbose_name="Membership Extension",
        model=MembershipExtension,
        form_class=MembershipExtensionForm,
        datatable_view=MembershipExtensionDataTableView,
        fields=[
            {"name": "membership", "label": "Membership", "type": "select", "required": True, "col": 6, "url_name": "member_membership_select"},
            {"name": "extra_days", "label": "Extra Days", "type": "number", "required": True, "col": 6, "min": 1, "step": 1},
            {"name": "approved_by", "label": "Approved By", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
            {"name": "reason", "label": "Reason", "type": "textarea", "required": False, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in MEMBERSHIP_EXTENSION_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
