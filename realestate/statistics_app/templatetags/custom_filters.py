from django import template

register = template.Library()

@register.filter(name='getattr')
def getattr(obj, attr_name):
    """
    Safely get an attribute of an object.
    This filter will return the value of the attribute with the given name.
    """
    try:
        if hasattr(obj, attr_name):
            return getattr(obj, attr_name)
    except Exception as e:
        # Optional: Log the error or handle it as needed
        return ''
    return ''


from django import template

register = template.Library()

@register.simple_tag
def get_field_value(obj, field_name):
    """
    Retrieve the value of a specified field from an object.
    """
    return obj.__getattribute__(field_name)