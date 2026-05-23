from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def range_filter(value):
    return range(int(value))


@register.filter
def subtract(value, arg):
    return int(value) - int(arg)