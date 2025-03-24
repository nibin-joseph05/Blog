from django import template
from django.urls import reverse

register = template.Library()

@register.filter
def notification_url(link):
    """Convert notification link format to actual URL."""
    if not link:
        return '#'
    
    try:
        # Split the link into namespace:name:slug
        parts = link.split(':')
        if len(parts) == 3:
            namespace, name, slug = parts
            return reverse(f'{namespace}:{name}', kwargs={'slug': slug})
    except:
        pass
    
    return '#' 