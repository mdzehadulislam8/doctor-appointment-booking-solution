"""
Custom template filters for doctors app
"""
from django import template

register = template.Library()


@register.filter
def split(value, separator):
    """Split a string by separator"""
    if value:
        return value.split(separator)
    return []
