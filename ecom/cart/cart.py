from store.models import Product 

class Cart: 
    def __init__(self, request): 
        self.session = request.session 
        cart = self.session.get('session_key') 
        if 'session_key' not in request.session: 
            cart = self.session['session_key'] = {} 
        self.cart = cart

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = int(quantity) 
        # Lógica para agregar el producto 
        if product_id in self.cart: 
            pass  # Si el producto ya está en el carrito, no hacemos nada (se mejorará en el futuro) 
        else: 
            # Si no existe, lo agregamos con la cantidad seleccionada
            self.cart[product_id] = int(product_qty) 
        self.session.modified = True 

    def __len__(self): 
        return len(self.cart)

    def get_prods(self):
        # Get ids from cart 
        product_ids = self.cart.keys()
        # Use ids to lookup products in database model 
        products = Product.objects.filter(id__in=product_ids)
        # Return those products 
        return products 

    def get_quants(self): 
        quantities = self.cart  
        return quantities 

    def update(self, product, quantity): 
        product_id = str(product) 
        product_qty = int(quantity) 

        # Get Cart 
        ourcart = self.cart  
        # Update dictionary 
        ourcart[product_id] = product_qty 

        self.session.modified = True 
        
        storecart = self.cart  
        return storecart 

    def delete(self, product): 
        product_id = str(product) 
        # Eliminar el producto del carrito si existe 
        if product_id in self.cart: 
            del self.cart[product_id] 
        self.session.modified = True 
