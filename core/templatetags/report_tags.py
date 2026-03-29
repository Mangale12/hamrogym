from django import template
from django.utils.html import conditional_escape


register = template.Library()


@register.filter
def get_item(value, key):
    if isinstance(value, dict):
        return value.get(key, "")
    return ""


@register.filter
def get_form_field(form, name):
    if form is None:
        return None
    try:
        return form[name]
    except Exception:
        return None


@register.filter
def has_advanced_blocks(blocks):
    return any((block or {}).get("advanced") for block in (blocks or []))


@register.filter
def render_report_value(value):
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, dict):
        if "label" in value:
            return value.get("label") or ""
        if "value" in value:
            return value.get("value") or ""
    return "" if value is None else value


@register.inclusion_tag("components/report/filter_field.html")
def render_report_field(form, field_config):
    config = dict(field_config or {})
    field_name = config.get("name", "")
    bound_field = get_form_field(form, field_name) if field_name else None
    field_type = (config.get("type") or "").strip().lower()
    is_hidden = bool(config.get("hidden")) or field_type == "hidden"
    wrapper_class = config.get("col") or "col-md-3"
    attrs = config.get("attrs") or {}
    data_attrs = config.get("data_attrs") or {}

    options = config.get("options") or []
    normalized_options = []
    for option in options:
        if isinstance(option, (list, tuple)) and len(option) >= 2:
            normalized_options.append({"value": option[0], "label": option[1]})
        elif isinstance(option, dict):
            normalized_options.append(
                {
                    "value": option.get("value", ""),
                    "label": option.get("label", option.get("value", "")),
                }
            )
        else:
            normalized_options.append({"value": option, "label": option})

    value = config.get("value", "")
    if bound_field is not None:
        value = bound_field.value()

    return {
        "config": config,
        "bound_field": bound_field,
        "field_name": field_name,
        "field_type": field_type or "text",
        "is_hidden": is_hidden,
        "wrapper_class": wrapper_class,
        "attrs": attrs,
        "data_attrs": data_attrs,
        "options": normalized_options,
        "value": value,
    }


@register.inclusion_tag("components/report/action_button.html")
def render_report_action(action, report_data=None, export_query=""):
    config = dict(action or {})
    requires_report_data = bool(config.get("requires_report_data"))
    show = not requires_report_data or report_data is not None
    kind = (config.get("kind") or "").strip().lower() or ("link" if config.get("href") or config.get("query_string") else "submit")
    attrs = config.get("attrs") or {}
    data_attrs = config.get("data_attrs") or {}

    href = config.get("href") or ""
    query_string = (config.get("query_string") or "").strip()
    if not href and query_string:
        href = f"?{export_query}&{query_string}" if export_query else f"?{query_string}"

    return {
        "show": show,
        "kind": kind,
        "href": href,
        "config": config,
        "attrs": attrs,
        "data_attrs": data_attrs,
    }


@register.filter
def html_attr(value):
    return conditional_escape(value)
