from django import template

from core.sidebar_loader import load_sidebar_items
from core.sidebar_loader import _normalize_items
from nepanest.products.hamrogym.sidebar import SIDEBAR_ITEMS as HAMROGYM_SIDEBAR_ITEMS

register = template.Library()


@register.inclusion_tag("core/sidebar.html", takes_context=True)
def render_sidebar(context):
    request = context.get("request")
    if not request:
        return {"sidebar_items": []}
    return {"sidebar_items": load_sidebar_items(request), "request": request}


@register.inclusion_tag("hamrogym/components/sidebar.html", takes_context=True)
def render_hamrogym_sidebar(context):
    request = context.get("request")
    if not request:
        return {"sidebar_items": []}

    path = request.path or "/"
    return {
        "sidebar_items": _normalize_items(HAMROGYM_SIDEBAR_ITEMS, path),
        "request": request,
    }
