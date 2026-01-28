from django import template
register = template.Library()

@register.filter
def sum_order_total(items):
    return sum([item.product.price * item.quantity for item in items])
