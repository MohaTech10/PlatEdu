from django import template
from MohTech.models import Orders

register = template.Library()

@register.filter
def cart_get_items(user):
    all_orders = Orders.objects.filter(user=user, is_ordered=False)
    if all_orders.exists():
        return all_orders[0].ordered_courses.all().count()
    return 0
# @register.filter
# def getCurrentOrder(user):
#     current_order = Orders.objects.get(user=user, is_ordered=False)
#     u = current_order.ordered_courses.all()
#     current_order_courses_in = [ordered_item.course for ordered_item in u]
#     print(current_order_courses_in)
#     return current_order_courses_in