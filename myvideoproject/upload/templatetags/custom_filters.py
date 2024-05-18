from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    old_value, new_value = arg.split(':')
    return value.replace(old_value, new_value)
