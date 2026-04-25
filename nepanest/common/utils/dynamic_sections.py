from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Dict, Iterable, List, Optional, Type

from django.db import models

from nepanest.common.helpers.helper import encode_date_for_display


SaveTransformer = Callable[[Any], Any]
LoadTransformer = Callable[[models.Model], Any]
RowSaveHook = Callable[[models.Model, Dict[str, Any], Any], None]
RowLoadHook = Callable[[models.Model], Dict[str, Any]]


@dataclass(frozen=True)
class RelatedDynamicSectionConfig:
    section_name: str
    related_model: Type[models.Model]
    parent_field: str
    fields: List[str]
    required_fields: Iterable[str] = field(default_factory=tuple)
    bool_fields: Iterable[str] = field(default_factory=tuple)
    empty_check_fields: Optional[Iterable[str]] = None
    include_files: bool = False
    order_by: str = "id"
    save_transformers: Dict[str, SaveTransformer] = field(default_factory=dict)
    load_transformers: Dict[str, LoadTransformer] = field(default_factory=dict)
    empty_value: Any = ""
    use_post_lists: bool = False
    row_save_hook: Optional[RowSaveHook] = None
    row_load_hook: Optional[RowLoadHook] = None


def parse_dynamic_section(
    request,
    section_name: str,
    include_files: bool = False,
    use_post_lists: bool = False,
) -> List[Dict[str, Any]]:
    pattern = re.compile(rf"^{re.escape(section_name)}\[(\d+)\]\[(.+)\]$")
    rows: Dict[int, Dict[str, Any]] = {}

    if use_post_lists:
        for key, values in request.POST.lists():
            match = pattern.match(key)
            if not match:
                continue
            index = int(match.group(1))
            field_name = match.group(2)
            rows.setdefault(index, {})[field_name] = values if len(values) > 1 else (values[0] if values else "")
    else:
        for key, value in request.POST.items():
            match = pattern.match(key)
            if not match:
                continue
            index = int(match.group(1))
            field_name = match.group(2)
            rows.setdefault(index, {})[field_name] = value

    if include_files:
        for key, value in request.FILES.items():
            match = pattern.match(key)
            if not match:
                continue
            index = int(match.group(1))
            field_name = match.group(2)
            rows.setdefault(index, {})[field_name] = value

    return [rows[idx] for idx in sorted(rows.keys())]


def to_bool(value: Any, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def build_related_section_saver(config: RelatedDynamicSectionConfig):
    def _save(request, parent_obj) -> None:
        rows = parse_dynamic_section(
            request,
            config.section_name,
            include_files=config.include_files,
            use_post_lists=config.use_post_lists,
        )
        existing = {
            item.id: item
            for item in config.related_model.objects.filter(**{config.parent_field: parent_obj})
        }
        keep_ids = []
        empty_check_fields = list(config.empty_check_fields or config.fields)
        required_fields = set(config.required_fields)
        bool_fields = set(config.bool_fields)

        for row in rows:
            item_id = row.get("id")
            item = None

            if item_id and str(item_id).isdigit():
                item = existing.get(int(item_id))

            if not item:
                item = config.related_model(**{config.parent_field: parent_obj})

            if hasattr(item, "fiscal_year_id") and not getattr(item, "fiscal_year_id", None):
                parent_fiscal_year_id = getattr(parent_obj, "fiscal_year_id", None)
                if parent_fiscal_year_id:
                    item.fiscal_year_id = parent_fiscal_year_id

            if not any(row.get(field_name) for field_name in empty_check_fields):
                continue

            if any(not row.get(field_name) for field_name in required_fields):
                continue

            for field_name in config.fields:
                raw_value = row.get(field_name)
                model_field = config.related_model._meta.get_field(field_name)

                if isinstance(model_field, models.FileField) and not raw_value:
                    continue

                if field_name in bool_fields:
                    value = to_bool(raw_value)
                else:
                    transformer = config.save_transformers.get(field_name)
                    value = transformer(raw_value) if transformer else raw_value
                if (
                    value == ""
                    and getattr(model_field, "null", False)
                    and not isinstance(model_field, (models.CharField, models.TextField, models.FileField))
                ):
                    value = None
                if isinstance(model_field, models.ForeignKey) and not isinstance(value, models.Model):
                    setattr(item, model_field.attname, value or None)
                else:
                    setattr(item, field_name, value)

            item.save()

            if config.row_save_hook:
                config.row_save_hook(item, row, parent_obj)

            keep_ids.append(item.id)

        queryset = config.related_model.objects.filter(**{config.parent_field: parent_obj})
        if keep_ids:
            queryset.exclude(id__in=keep_ids).delete()
        else:
            queryset.delete()

    return _save


def build_related_section_loader(config: RelatedDynamicSectionConfig):
    def _load(parent_obj, request=None) -> Dict[str, List[Dict[str, Any]]]:
        rows = []
        queryset = config.related_model.objects.filter(**{config.parent_field: parent_obj}).order_by(
            config.order_by
        )

        for item in queryset:
            row = {"id": item.id}
            for field_name in config.fields:
                transformer = config.load_transformers.get(field_name)
                if transformer:
                    row[field_name] = transformer(item)
                    continue
                model_field = config.related_model._meta.get_field(field_name)
                if isinstance(model_field, models.ForeignKey):
                    value = getattr(item, model_field.attname, config.empty_value)
                    row[field_name] = config.empty_value if value is None else str(value)
                    continue
                if isinstance(model_field, models.FileField):
                    value = getattr(item, field_name, None)
                    row[field_name] = (
                        {
                            "name": value.name,
                            "url": getattr(value, "url", ""),
                        }
                        if value
                        else config.empty_value
                    )
                    continue
                value = getattr(item, field_name, config.empty_value)
                if isinstance(value, date):
                    row[field_name] = encode_date_for_display(value, request)
                else:
                    row[field_name] = config.empty_value if value is None else value
            if config.row_load_hook:
                row.update(config.row_load_hook(item))
            rows.append(row)

        return {config.section_name: rows}

    return _load
