from datetime import date

from django import template
from django.forms import widgets as form_widgets
from django.utils.dateparse import parse_date
from django.utils.html import conditional_escape

from core.helpers.helper import encode_date_for_display


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


@register.inclusion_tag("components/report/filter_field.html", takes_context=True)
def render_report_field(context, form, field_config):
    config = dict(field_config or {})
    request = context.get("request")
    field_name = config.get("name", "")
    bound_field = get_form_field(form, field_name) if field_name else None
    field_type = (config.get("type") or "").strip().lower()
    widget = getattr(getattr(bound_field, "field", None), "widget", None)
    widget_type = (getattr(widget, "input_type", "") or "").strip().lower()
    is_hidden = bool(config.get("hidden")) or field_type == "hidden" or isinstance(widget, form_widgets.HiddenInput)
    wrapper_class = config.get("col") or "col-md-3"
    attrs = dict(config.get("attrs") or {})
    widget_attrs = {}
    if widget is not None:
        widget_attrs = dict(getattr(widget, "attrs", {}))
        attrs = {**widget_attrs, **attrs}
    data_attrs = config.get("data_attrs") or {}
    for key, value in data_attrs.items():
        attrs[f"data-{key}"] = value
    for reserved_key in ("class", "id", "placeholder", "min", "max", "step", "type", "rows", "style"):
        attrs.pop(reserved_key, None)

    label = config.get("label") or getattr(bound_field, "label", "") or field_name.replace("_", " ").title()
    field_id = config.get("id") or getattr(bound_field, "id_for_label", "") or f"report-field-{field_name}"
    required = config.get("required")
    if required is None and bound_field is not None:
        required = bool(getattr(bound_field.field, "required", False))
    help_text = config.get("help_text")
    if help_text is None and bound_field is not None:
        help_text = getattr(bound_field, "help_text", "")
    errors = []
    if bound_field is not None:
        errors = [str(error) for error in bound_field.errors]

    options = config.get("options") or []
    data_url = config.get("url") or config.get("data_url")
    if bound_field is not None and hasattr(bound_field.field, "choices") and not data_url:
        options = list(bound_field.field.choices)
    normalized_options = []
    empty_label = config.get("empty_label")
    for option in options:
        if isinstance(option, (list, tuple)) and len(option) >= 2:
            if option[0] in ("", None) and empty_label is None:
                empty_label = option[1]
                continue
            normalized_options.append((option[0], option[1]))
        elif isinstance(option, dict):
            option_value = option.get("value", "")
            option_label = option.get("label", option.get("value", ""))
            if option_value in ("", None) and empty_label is None:
                empty_label = option_label
                continue
            normalized_options.append((option_value, option_label))
        else:
            normalized_options.append((option, option))

    value = config.get("value", "")
    if bound_field is not None:
        value = bound_field.value()

    multiple = bool(config.get("multiple"))
    if widget is not None and getattr(widget, "allow_multiple_selected", False):
        multiple = True

    if field_type in {"textarea"} or isinstance(widget, form_widgets.Textarea):
        component_type = "textarea"
        component_template = "components/forms/textarea.html"
    elif field_type in {"checkbox", "switch"} or isinstance(widget, form_widgets.CheckboxInput):
        component_type = "checkbox"
        component_template = "components/forms/checkbox.html"
    elif field_type in {"select", "static_select"} or isinstance(widget, (form_widgets.Select, form_widgets.SelectMultiple)):
        component_type = "select"
        component_template = "components/forms/select.html"
    elif field_type == "date" or isinstance(widget, form_widgets.DateInput):
        component_type = "date"
        component_template = "components/forms/datepicker.html"
    else:
        component_type = "input"
        component_template = "components/forms/input.html"

    input_type = field_type or widget_type or "text"
    if component_type == "input" and isinstance(widget, form_widgets.DateTimeInput):
        input_type = "datetime-local"
    elif component_type == "input" and isinstance(widget, form_widgets.TimeInput):
        input_type = "time"

    checked = False
    if component_type == "checkbox":
        checked = bool(value)

    display_value = value
    if component_type == "date" and value not in (None, ""):
        parsed_value = value if isinstance(value, date) else parse_date(str(value))
        if parsed_value is not None:
            display_value = encode_date_for_display(parsed_value, request)

    return {
        "config": config,
        "bound_field": bound_field,
        "request": request,
        "is_bs_calendar": context.get("is_bs_calendar", False),
        "is_ad_calendar": context.get("is_ad_calendar", False),
        "calendar_type": context.get("calendar_type", ""),
        "field_name": field_name,
        "field_type": field_type or widget_type or "text",
        "is_hidden": is_hidden,
        "wrapper_class": wrapper_class,
        "attrs": attrs,
        "options": normalized_options,
        "value": display_value,
        "label": label,
        "field_id": field_id,
        "required": required,
        "help_text": help_text,
        "errors": errors,
        "empty_label": empty_label,
        "multiple": multiple,
        "checked": checked,
        "component_type": component_type,
        "component_template": component_template,
        "input_type": input_type,
        "input_class": config.get("input_class", widget_attrs.get("class", "")),
        "placeholder": config.get("placeholder", widget_attrs.get("placeholder", "")),
        "rows": config.get("rows", widget_attrs.get("rows")),
        "style": config.get("style", widget_attrs.get("style")),
        "min_value": config.get("min", widget_attrs.get("min")),
        "max_value": config.get("max", widget_attrs.get("max")),
        "step": config.get("step", widget_attrs.get("step")),
        "prefix": config.get("prefix"),
        "suffix": config.get("suffix"),
        "data_field_name": config.get("data_field_name") or field_name,
        "data_url": data_url,
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
