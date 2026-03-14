"""Backward-compatible aliases for Fiscal Year views.

The core app now uses config-driven, reusable views. These aliases allow
imports like `from core.views.fiscal_year import FiscalYearListView` to
keep working if they exist elsewhere.
"""

from core.registry import get_entity_config
from core.views.entities import build_entity_views

_entity = get_entity_config("currency")
_views = build_entity_views(_entity)

CurrencyListView = _views["list_view"]
CurrencyDetailView = _views["detail_view"]
CurrencyCreateView = _views["create_view"]
CurrencyUpdateView = _views["update_view"]
CurrencyDeleteView = _views["delete_view"]
CurrencyDataTableView = _views["datatable_view"]
CurrencySelectView = _views["select_view"]
