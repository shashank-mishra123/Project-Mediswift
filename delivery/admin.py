from django.contrib import admin
from .models import DeliveryBoy

@admin.register(DeliveryBoy)
class DeliveryBoyAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'vehicle_number', 'status', 'total_deliveries', 'rating']
    list_filter = ['status']
    search_fields = ['name', 'phone', 'vehicle_number']
