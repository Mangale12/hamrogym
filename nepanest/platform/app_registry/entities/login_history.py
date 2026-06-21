from core.config import EntityConfig
from core.registry import register_entity
from ..datatables.login_history_data_table import LoginHistoryDataTableView, LOGIN_HISTORY_COLUMNS
from ..forms.login_history_form import LoginHistoryForm
from ..models import LoginHistory


register_entity(
    EntityConfig(
        name="login_history",
        url_path="login-history",
        verbose_name="Login History",
        model=LoginHistory,
        form_class=LoginHistoryForm,
        datatable_view=LoginHistoryDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LOGIN_HISTORY_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
