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
            {"name": "membership", "label": "Membership", "type": "select", "required": True, "col": 6, "url_name": "membership_list"},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": True, "col": 6},
            {"name": "end_date", "label": "End Date", "type": "date", "required": True, "col": 6},
            {"name": "total_days", "label": "Total Days", "type": "number", "required": True, "col": 6},
            {"name": "reason", "label": "Reason", "type": "textarea", "required": False, "col": 6},
            {"name": "approved_by", "label": "Approved By", "type": "select", "required": True, "col": 6, "url_name": "user_list"},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in MEMBERSHIP_EXTENSION_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
