from django.contrib import admin

from orders.models import Cart, CartItem, Order, OrderItem, TGUser


@admin.register(TGUser)
class TGUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name', 'username')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('tg_user', 'total_price')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('tg_user', 'delivery_address', 'phone_number', 'is_paid')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
