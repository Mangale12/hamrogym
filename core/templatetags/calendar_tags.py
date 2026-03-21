from django import template

from core.helpers.helper import encode_date_for_display, get_calendar_type


register = template.Library()


@register.simple_tag(takes_context=True)
def display_date(context, value, fallback=""):
    request = context.get("request")
    if not value:
        return fallback
    return encode_date_for_display(value, request)


@register.simple_tag(takes_context=True)
def active_calendar_type(context, fallback="AD"):
    request = context.get("request")
    return get_calendar_type(request) if request else fallback
