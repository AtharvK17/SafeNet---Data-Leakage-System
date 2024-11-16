from django import template

register = template.Library()

@register.filter
def get_item(list_object, index):
    try:
        return list_object[index]
    except:
        return ''