from core.config import EntityConfig
from core.datatables import CurrencyDataTableView
from core.forms import CurrencyForm
from nepanest.foundation.fiscal import Currency
from core.registry import register_entity


register_entity(
    EntityConfig(
        name="currency",
        url_path="currencies",
        verbose_name="Currency",
        model=Currency,
        form_class=CurrencyForm,
        datatable_view=CurrencyDataTableView,
        fields=[
            {
                "name": "code",
                "label": "Currency Code",
                "type": "text",
                "required": True,
                "col": 4,
                "placeholder": "USD",
            },
            {
                "name": "name",
                "label": "Currency Name",
                "type": "text",
                "required": True,
                "col": 4,
                "placeholder": "US Dollar",
            },
            {
                "name": "symbol",
                "label": "Currency Symbol",
                "type": "text",
                "required": True,
                "col": 4,
                "placeholder": "$",
            },
        ],
        datatable_columns=[
            {"name": "code", "title": "Code"},
            {"name": "name", "title": "Name"},
            {"name": "symbol", "title": "Symbol"},
        ],
        reset_defaults={},
    )
)
