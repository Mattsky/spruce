from django import template

register = template.Library()

@register.simple_tag
def extract_hostname(value):
    return value.split("_")[0]
