from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'experience', 'fees', 'status']
    list_filter = ['specialty', 'status']
    search_fields = ['name', 'specialty', 'hospital']
