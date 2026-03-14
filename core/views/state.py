"""Backward-compatible aliases for State views."""

from core.registry import get_entity_config
from core.views.entities import build_entity_views

_entity = get_entity_config("state")
_views = build_entity_views(_entity)

StateListView = _views["list_view"]
StateDetailView = _views["detail_view"]
StateCreateView = _views["create_view"]
StateUpdateView = _views["update_view"]
StateDeleteView = _views["delete_view"]
StateDataTableView = _views["datatable_view"]
StateSelectView = _views["select_view"]
