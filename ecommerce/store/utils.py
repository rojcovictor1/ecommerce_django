import json

from .models import *


def cookie_cart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except KeyError:
        cart = {}

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cart_items = order['get_cart_items']

    for item in cart:
        try:
            cart_items += cart[item]['quantity']
            product = Product.objects.get(id=item)
            total = (product.price * cart[item]['quantity'])
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[item]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image_url': product.image_url
                },
                'quantity': cart[item]['quantity'],
                'get_total': total
            }
            items.append(item)

            if product.digital == 'False':
                order['shipping'] = True
        except KeyError:
            pass
    return {'cartItems': cart_items, 'order': order, 'items': items}


def cart_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
    else:
        cookie_data = cookie_cart(request)
        cart_items = cookie_data['cartItems']
        order = cookie_data['order']
        items = cookie_data['items']
    return {'cartItems': cart_items, 'order': order, 'items': items}


def guest_order(request, data):
    name = data['form']['name']
    email = data['form']['email']
    cookie_data = cookie_cart(request)
    items = cookie_data['items']

    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=True,
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    return customer, order
