from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.policy_data_table import PolicyDataTableView, POLICY_COLUMNS
from ...forms.policy_form import PolicyForm
from ...models import Policy


register_entity(
    EntityConfig(
        name="policy",
        url_path="policies",
        verbose_name="Policies",
        model=Policy,
        form_class=PolicyForm,
        datatable_view=PolicyDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in POLICY_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
