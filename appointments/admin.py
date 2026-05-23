from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['booking_ref', 'patient_name', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date']
    search_fields = ['patient_name', 'booking_ref', 'patient_mobile']
