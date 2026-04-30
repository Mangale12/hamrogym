from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.member_tag_data_table import MemberTagDataTableView, MEMBER_TAG_COLUMNS
from ...forms.member_tag_form import MemberTagForm
from ...models import MemberTag


register_entity(
    EntityConfig(
        name="member_tag",
        url_path="member-tags",
        verbose_name="Member Tag",
        model=MemberTag,
        form_class=MemberTagForm,
        datatable_view=MemberTagDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in MEMBER_TAG_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
