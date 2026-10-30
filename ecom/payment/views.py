from django.shortcuts import render, redirect
from django.contrib import messages
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User

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
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        payment_form = PaymentForm(request.POST or None)
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

        # Crear la orden con los datos recopilados
        if request.user.is_authenticated:
            # Está logueado
            user = request.user
            create_order = Order(
                user=user,
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid
            )
            create_order.save()

            messages.success(request, "Order Placed Successfully")
            return redirect('home')

        else:
            # No está logueado
            create_order = Order(
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid
            )
            create_order.save()

            messages.success(request, "Order Placed Successfully")
            return redirect('home')

    else:
        messages.error(request, "Access Denied")
        return redirect('home')
