from django.contrib import admin
from .models import Cart, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method']
    search_fields = ['order_number']
    inlines = [OrderItemInline]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'added_at']
