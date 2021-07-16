from django import template
from my_site.models import ShoppingCartOrder

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = ShoppingCartOrder.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    else:
        return 0