from django import template

from core.sidebar_loader import load_sidebar_items

register = template.Library()


@register.inclusion_tag("core/sidebar.html", takes_context=True)
def render_sidebar(context):
    request = context.get("request")
    if not request:
        return {"sidebar_items": []}
    return {"sidebar_items": load_sidebar_items(request), "request": request}
