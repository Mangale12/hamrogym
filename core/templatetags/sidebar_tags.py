from django import template

from core.sidebar_loader import load_sidebar_items
from core.sidebar_loader import _normalize_items
from nepanest.products.hamrogym.sidebar import SIDEBAR_ITEMS as HAMROGYM_SIDEBAR_ITEMS
from nepanest.modules.crm.sidebar import SIDEBAR_ITEMS as CRM_SIDEBAR_ITEMS
from nepanest.platform.app_registry.sidebar import SIDEBAR_ITEMS as APP_REGISTRY_SIDEBAR_ITEMS

register = template.Library()


@register.inclusion_tag("core/sidebar.html", takes_context=True)
def render_sidebar(context):
    request = context.get("request")
    if not request:
        return {"sidebar_items": []}
    # Strict namespace check: only use the registry sidebar when the resolver
    # namespace explicitly matches the registry namespaces. This avoids path
    # heuristics and ensures predictable behaviour when URL routing changes.
    path = request.path or "/"
    resolver_ns = None
    if getattr(request, "resolver_match", None):
        resolver_ns = request.resolver_match.namespace

    if resolver_ns in ("registry", "app_registry", "register"):
        return {"sidebar_items": _normalize_items(APP_REGISTRY_SIDEBAR_ITEMS, path, request), "request": request}

    return {"sidebar_items": load_sidebar_items(request), "request": request}


@register.inclusion_tag("hamrogym/components/sidebar.html", takes_context=True)
def render_hamrogym_sidebar(context):
    request = context.get("request")
    if not request:
        return {"sidebar_items": []}

    path = request.path or "/"
    return {
        "sidebar_items": _normalize_items(HAMROGYM_SIDEBAR_ITEMS, path, request),
        "request": request,
    }


@register.inclusion_tag("crm/components/sidebar.html", takes_context=True)
def render_crm_sidebar(context):
    request = context.get("request")
    if not request:
        return {"sidebar_items": []}

    path = request.path or "/"
    return {
        "sidebar_items": _normalize_items(CRM_SIDEBAR_ITEMS, path, request),
        "request": request,
    }
