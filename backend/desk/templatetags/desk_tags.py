from django import template

from desk.presentation import money

register = template.Library()
register.filter("money", money)


@register.filter
def item(mapping, key):
    return mapping.get(key, "")
