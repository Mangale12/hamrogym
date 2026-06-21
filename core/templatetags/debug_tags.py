from django import template

from nepanest.common.helpers.debug_helper import dd, ddump


register = template.Library()


@register.simple_tag(name="dd")
def dd_tag(*args):
    return dd(*args)


@register.simple_tag(name="ddump")
def ddump_tag(obj, label=""):
    ddump(obj, label=label)
    return ""
