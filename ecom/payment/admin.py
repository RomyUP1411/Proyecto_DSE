from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem

# Registrar modelos en el panel de administración
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)
