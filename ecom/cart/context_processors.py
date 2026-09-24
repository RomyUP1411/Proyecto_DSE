from .cart import Cart 

# Context processor para que el carrito esté disponible en todas las páginas 
def cart(request): 
    return {'cart': Cart(request)}
