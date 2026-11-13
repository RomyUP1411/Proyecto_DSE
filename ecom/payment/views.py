from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from store.models import Product, Profile
import datetime
import random

# Vista para pago exitoso
def payment_success(request):
    return render(request, "payment/payment_success.html", {})

# Vista para pago fallido
def payment_failed(request):
    return render(request, "payment/payment_failed.html", {})

def checkout(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        # Si el usuario está logueado
        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        return render(
            request,
            "payment/checkout.html",
            {
                'cart_products': cart_products,
                'quantities': quantities,
                'totals': totals,
                'shipping_form': shipping_form
            }
        )
    else:
        # Si solo es visitante
        shipping_form = ShippingForm(request.POST or None)

        return render(
            request,
            "payment/checkout.html",
            {
                'cart_products': cart_products,
                'quantities': quantities,
                'totals': totals,
                'shipping_form': shipping_form
            }
        )

def billing_info(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        # Guardar la información de envío en la sesión
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            billing_form = PaymentForm()
            return render(
                request,
                "payment/billing_info.html",
                {
                    'cart_products': cart_products,
                    'quantities': quantities,
                    'totals': totals,
                    'shipping_info': request.POST,
                    'billing_form': billing_form,
                }
            )
        else:
            billing_form = PaymentForm()
            return render(
                request,
                "payment/billing_info.html",
                {
                    'cart_products': cart_products,
                    'quantities': quantities,
                    'totals': totals,
                    'shipping_info': request.POST,
                    'billing_form': billing_form,
                }
            )

    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def proccess_order(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        card_credit = random.randint(int(totals - 100), int(totals + 100))
        payment_form = PaymentForm(request.POST or None)

        # Get shipping info from session
        my_shipping = request.session.get('my_shipping')
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = (
            f"{my_shipping['shipping_address1']}\n"
            f"{my_shipping.get('shipping_address2', '')}\n"
            f"{my_shipping['shipping_city']}\n"
            f"{my_shipping.get('shipping_state', '')}\n"
            f"{my_shipping.get('shipping_zipcode', '')}\n"
            f"{my_shipping['shipping_country']}"
        )

        amount_paid = totals
        user = request.user if request.user.is_authenticated else None

        # Create order
        create_order = Order(
            user=user,
            full_name=full_name,
            email=email,
            shipping_address=shipping_address,
            amount_paid=amount_paid
        )
        create_order.save()

        # Add order items
        order_id = create_order.pk
        for product in cart_products():
            product_id = product.id
            price = product.sale_price if product.is_sale else product.price

            for key, value in quantities().items():
                if int(key) == product.id:
                    create_order_item = OrderItem(
                        order_id=order_id,
                        product_id=product_id,
                        user=user,
                        quantity=value,
                        price=price
                    )
                    create_order_item.save()

        # Delete the shopping cart
        for key in list(request.session.keys()):
            if key == "session_key":
                del request.session[key]

        # Delete cart from Database (old_cart field)
        if request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")

        messages.success(request, "Order Placed Successfully")
        return render(
            request,
            "payment/proccess_order.html",
            {
                'cart_products': cart_products,
                'quantities': quantities,
                'totals': totals,
                'card_credit': card_credit,
                'shipping_info': my_shipping,
                'payment_info': request.POST
            }
        )

    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        # Obtener todas las órdenes no enviadas
        orders = Order.objects.filter(shipped=False)

        if request.POST:
            status = request.POST.get('shipping_status')
            num = request.POST.get('num')

            # Obtener la orden específica
            order = Order.objects.filter(id=num)

            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=now)

            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/not_shipped_dash.html", {'orders': orders})

    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        # Obtener todas las órdenes enviadas
        orders = Order.objects.filter(shipped=True)

        if request.POST:
            status = request.POST.get('shipping_status')
            num = request.POST.get('num')

            # Obtener la orden específica
            order = Order.objects.filter(id=num)

            # Actualizar el estado a no enviado
            order.update(shipped=False)

            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/shipped_dash.html", {'orders': orders})

    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Obtener la orden y sus items
        order = get_object_or_404(Order, id=pk)
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST.get('shipping_status')

            if status == "true":
                now = datetime.datetime.now()
                Order.objects.filter(id=pk).update(shipped=True, date_shipped=now)
            else:
                Order.objects.filter(id=pk).update(shipped=False)

            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/orders.html", {'order': order, 'items': items})

    else:
        messages.success(request, "Access Denied")
        return redirect('home')
