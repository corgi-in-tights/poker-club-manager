from django import template

register = template.Library()


@register.simple_tag
def querystring(request, **kwargs):
    params = request.GET.copy()

    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value

    return params.urlencode()
