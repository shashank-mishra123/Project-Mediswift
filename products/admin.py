from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'icon']
    search_fields = ['name', 'display_name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'discount_percent', 'prescription_required', 'is_active']
    list_filter = ['category', 'prescription_required', 'is_active']
    search_fields = ['name', 'manufacturer', 'description']
