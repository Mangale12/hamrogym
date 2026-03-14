from importlib import import_module

from django.apps import apps
from django.urls import NoReverseMatch, reverse


def _resolve_item_url(item):
    url = item.get("url")
    url_name = item.get("url_name")
    if (not url or url == "#") and url_name:
        try:
            url = reverse(url_name)
        except NoReverseMatch:
            url = "#"
    item["url"] = url


def _apply_active_state(item, path):
    match = item.get("match") or item.get("url")
    if match in (None, "", "#"):
        item["is_active"] = False
    elif match == "/":
        item["is_active"] = path == "/"
    else:
        item["is_active"] = path.startswith(match.rstrip("/"))


def _normalize_items(items, path):
    normalized = []
    for raw in items or []:
        item = dict(raw)
        _resolve_item_url(item)
        children = item.get("children") or []
        if children:
            item["children"] = _normalize_items(children, path)
            item["is_active"] = any(child.get("is_active") for child in item["children"])
        else:
            _apply_active_state(item, path)
        normalized.append(item)
    return normalized


def load_sidebar_items(request):
    items = []
    for app_config in apps.get_app_configs():
        module_name = f"{app_config.name}.sidebar"
        try:
            module = import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name:
                continue
            raise

        app_items = getattr(module, "SIDEBAR_ITEMS", None)
        if app_items:
            items.extend(app_items)

    path = request.path or "/"
    return _normalize_items(items, path)
