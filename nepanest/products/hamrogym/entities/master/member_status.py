from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.member_status_data_table import MEMBER_STATUS_COLUMNS, MemberStatusDataTableView
from ...forms.member_status_form import MemberStatusForm
from ...models import MemberStatus


register_entity(
    EntityConfig(
        name="member_status",
        url_path="member-statuses",
        verbose_name="Member Status",
        model=MemberStatus,
        form_class=MemberStatusForm,
        datatable_view=MemberStatusDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in MEMBER_STATUS_COLUMNS
            if key != "id"
        ],
        select_search_fields=["name", "code", "remarks"],
        action_state_field="is_system",
        hide_delete_on_values=["true"],
        reset_defaults={"is_active": True},
    )
)
