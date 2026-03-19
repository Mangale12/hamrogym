from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

from django import forms
from django.db import models
from django.views import View


@dataclass(frozen=True)
class EntityConfig:
    name: str
    verbose_name: str
    model: Type[models.Model]
    form_class: Type[forms.ModelForm]
    datatable_view: Type[View]
    fields: List[Dict[str, Any]]
    datatable_columns: List[Dict[str, Any]]
    url_path: Optional[str] = None
    template_name: str = "core/entity_index.html"
    reset_defaults: Dict[str, Any] = field(default_factory=dict)
    tabs: Optional[List[Dict[str, Any]]] = None
    dynamic_sections: Optional[Dict[str, Any]] = None
    dynamic_sections_loader: Optional[Callable[[models.Model], Dict[str, Any]]] = None
    dynamic_sections_saver: Optional[Callable[[models.Model, Any], None]] = None
    post_save: Optional[Callable[[models.Model, Any], None]] = None
    row_actions: Dict[str, Callable[[Any, models.Model], Any]] = field(default_factory=dict)
    action_state_field: Optional[str] = None
    hide_edit_on_values: List[Any] = field(default_factory=list)
    hide_delete_on_values: List[Any] = field(default_factory=list)
    select_search_fields: Optional[List[str]] = None
    select_label_field: Optional[str] = None
    select_label_func: Optional[Callable[[models.Model], str]] = None
    select_page_size: int = 20
    select_order_by: Optional[str] = None
    action_buttons: List[Dict[str, Any]] = field(default_factory=list)
    show_actions: bool = True
    show_create: bool = True
    show_view: bool = True

    @property
    def url_base(self) -> str:
        return self.url_path or self.name.replace("_", "-")

    def _has_field(self, field_name: str) -> bool:
        try:
            self.model._meta.get_field(field_name)
            return True
        except Exception:
            return False

    def get_select_search_fields(self) -> List[str]:
        if self.select_search_fields:
            return self.select_search_fields
        searchable = getattr(self.datatable_view, "searchable_columns", None)
        if searchable:
            return list(searchable)
        if self._has_field("name"):
            return ["name"]
        return ["id"]

    def get_select_label(self, obj: models.Model) -> str:
        if self.select_label_func:
            return self.select_label_func(obj)
        if self.select_label_field:
            return str(getattr(obj, self.select_label_field, obj))
        return str(obj)

    def get_select_order_by(self) -> str:
        if self.select_order_by:
            return self.select_order_by
        if self._has_field("name"):
            return "name"
        return "id"
