from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Type

from django.db import models


SaveTransformer = Callable[[Any], Any]
LoadTransformer = Callable[[models.Model], Any]


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


def parse_dynamic_section(request, section_name: str, include_files: bool = False) -> List[Dict[str, Any]]:
    pattern = re.compile(rf"^{re.escape(section_name)}\[(\d+)\]\[(.+)\]$")
    rows: Dict[int, Dict[str, Any]] = {}

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

            if not any(row.get(field_name) for field_name in empty_check_fields):
                continue

            if any(not row.get(field_name) for field_name in required_fields):
                continue

            for field_name in config.fields:
                raw_value = row.get(field_name)
                if field_name in bool_fields:
                    value = to_bool(raw_value)
                else:
                    transformer = config.save_transformers.get(field_name)
                    value = transformer(raw_value) if transformer else raw_value
                setattr(item, field_name, value)

            item.save()
            keep_ids.append(item.id)

        queryset = config.related_model.objects.filter(**{config.parent_field: parent_obj})
        if keep_ids:
            queryset.exclude(id__in=keep_ids).delete()
        else:
            queryset.delete()

    return _save


def build_related_section_loader(config: RelatedDynamicSectionConfig):
    def _load(parent_obj) -> Dict[str, List[Dict[str, Any]]]:
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
                value = getattr(item, field_name, config.empty_value)
                row[field_name] = config.empty_value if value is None else value
            rows.append(row)

        return {config.section_name: rows}

    return _load
