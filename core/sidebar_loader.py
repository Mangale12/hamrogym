from importlib import import_module

from django.apps import apps
from django.urls import NoReverseMatch, reverse


def _user_has_permission(request, permission):
    if not permission:
        return True

    user = getattr(request, "user", None)
    return bool(user and user.is_authenticated and user.has_perm(permission))


def _resolve_item_url(item):
    url = item.get("url")
    url_name = item.get("url_name")
    if (not url or url == "#") and url_name:
        try:
            namespace = item.get("namespace")
            if namespace:
                try:
                    url = reverse(f"{namespace}:{url_name}")
                except NoReverseMatch:
                    # fall back to plain name if namespaced reverse not found
                    url = reverse(url_name)
            else:
                url = reverse(url_name)
        except NoReverseMatch:
            url = "#"
    item["url"] = url


def _normalize_item(item, path, request):
    item.setdefault("icon", "circle")
    item.setdefault("permission", "")
    item.setdefault("children", [])
    item.setdefault("url", "#")

    if not _user_has_permission(request, item.get("permission")):
        return None

    _resolve_item_url(item)
    children = item.get("children") or []
    if children:
        item["children"] = _normalize_items(children, path, request)
        item["is_active"] = any(child.get("is_active") for child in item["children"])
    else:
        item["children"] = []
        _apply_active_state(item, path)

    if item.get("children") == [] and item.get("url") in (None, ""):
        item["url"] = "#"

    return item


def _apply_active_state(item, path):
    match = item.get("match") or item.get("url")
    if match in (None, "", "#"):
        item["is_active"] = False
    elif match == "/":
        item["is_active"] = path == "/"
    else:
        item["is_active"] = path.startswith(match.rstrip("/"))


def _normalize_items(items, path, request=None):
    normalized = []
    for raw in items or []:
        item = dict(raw)
        normalized_item = _normalize_item(item, path, request)
        if normalized_item is not None:
            normalized.append(normalized_item)
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
    return _normalize_items(items, path, request)
