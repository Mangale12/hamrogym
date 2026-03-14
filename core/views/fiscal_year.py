"""Backward-compatible aliases for Fiscal Year views.

The core app now uses config-driven, reusable views. These aliases allow
imports like `from core.views.fiscal_year import FiscalYearListView` to
keep working if they exist elsewhere.
"""

from core.registry import get_entity_config
from core.views.entities import build_entity_views

_entity = get_entity_config("fiscal_year")
_views = build_entity_views(_entity)

FiscalYearListView = _views["list_view"]
FiscalYearDetailView = _views["detail_view"]
FiscalYearCreateView = _views["create_view"]
FiscalYearUpdateView = _views["update_view"]
FiscalYearDeleteView = _views["delete_view"]
FiscalYearDataTableView = _views["datatable_view"]
FiscalYearSelectView = _views["select_view"]
