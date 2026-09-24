from django.shortcuts import render, get_object_or_404 
from .cart import Cart  
from store.models import Product 
from django.http import JsonResponse 
from django.contrib import messages

def cart_summary(request): 
    # Obtener el carrito 
    cart = Cart(request) 
    # Obtener los productos del carrito 
    cart_products = cart.get_prods() 
    quantities = cart.get_quants() 
    return render(request, "cart_summary.html", {'cart_products': cart_products, 'quantities': quantities}) 

def cart_add(request): 
    # Get the cart 
    cart = Cart(request) 
    # test for POST 
    if request.POST.get('action') == 'post': 
        # Get elements 
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        # Lookup for product 
        product = get_object_or_404(Product, id=product_id) 
        # Save to session 
        cart.add(product=product, quantity=product_qty) 
        # Get Cart Quantity 
        cart_quantity = cart.__len__() 
        # Return responde 
        response = JsonResponse({'qty': cart_quantity}) 
        messages.success(request, ("Product Added To The Shopping Cart")) 
        return response 

def cart_delete(request): 
    cart = Cart(request) 
    if request.POST.get('action') == 'post': 
        # Obtener el ID del producto 
        product_id = int(request.POST.get('product_id')) 
        # Llamar a la función delete en cart.py 
        cart.delete(product=product_id) 
        # Responder con el ID del producto eliminado 
        response = JsonResponse({'product': product_id}) 
        return response 

def cart_update(request): 
    cart = Cart(request) 
    if request.POST.get('action') == 'post': 
        # Get elements 
        product_id = int(request.POST.get('product_id')) 
        product_qty = int(request.POST.get('product_qty')) 
        
        cart.update(product=product_id, quantity=product_qty) 
        
        response = JsonResponse({'qty': product_qty}) 
        return response 
