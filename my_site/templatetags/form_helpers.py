from django import template


register = template.Library()

@register.simple_tag
def render_label(bound_field, css_class):
    return bound_field.label_tag(attrs={'class': css_class})