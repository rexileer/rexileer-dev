from django import template

from desk.presentation import money

register = template.Library()
register.filter("money", money)


@register.filter
def review_number(value):
    if value is None:
        return "Неизвестно"
    return format(value.normalize(), ",f").replace(",", " ").replace(".", ",")


@register.filter
def item(mapping, key):
    return mapping.get(key, "")
