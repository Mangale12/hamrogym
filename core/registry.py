from importlib import import_module
from typing import List

from django.apps import apps

from core.config import EntityConfig

_REGISTRY: List[EntityConfig] = []


def register_entity(entity: EntityConfig) -> EntityConfig:
    existing = {item.name for item in _REGISTRY}
    if entity.name in existing:
        raise ValueError(f"Entity already registered: {entity.name}")
    _REGISTRY.append(entity)
    return entity


def get_entities() -> List[EntityConfig]:
    return list(_REGISTRY)


def get_entity_config(name: str) -> EntityConfig:
    for entity in _REGISTRY:
        if entity.name == name:
            return entity
    raise KeyError(f"Unknown entity: {name}")


def autodiscover_entities() -> None:
    for app_config in apps.get_app_configs():
        module_name = f"{app_config.name}.entities"
        try:
            import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name:
                continue
            raise
