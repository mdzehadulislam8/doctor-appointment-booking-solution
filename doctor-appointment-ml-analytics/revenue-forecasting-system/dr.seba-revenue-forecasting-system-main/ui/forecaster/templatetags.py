"""
Custom Django filters for templates
"""
from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiply value by argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Divide value by argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def enumerate(iterable):
    """Add enumerate to template"""
    return enumerate(iterable)
