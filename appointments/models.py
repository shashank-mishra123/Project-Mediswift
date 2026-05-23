from django.db import models
from django.conf import settings
import random, string


def gen_booking_ref():
    return 'BK' + ''.join(random.choices(string.digits, k=8))


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    doctor = models.ForeignKey(
        'doctors.Doctor', on_delete=models.CASCADE, related_name='appointments'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='appointments'
    )
    patient_name = models.CharField(max_length=100)
    patient_mobile = models.CharField(max_length=15)
    appointment_date = models.DateField()
    appointment_time = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    booking_ref = models.CharField(max_length=20, unique=True, default=gen_booking_ref)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['-appointment_date', '-created_at']

    def __str__(self):
        return f"{self.booking_ref} — {self.patient_name} with Dr. {self.doctor.name}"

    @property
    def is_upcoming(self):
        """Check if appointment is upcoming"""
        from datetime import date
        return self.appointment_date >= date.today()

    @property
    def is_today(self):
        """Check if appointment is today"""
        from datetime import date
        return self.appointment_date == date.today()

    @property
    def can_cancel(self):
        """Check if appointment can be cancelled"""
        return self.status in ['Pending', 'Confirmed'] and self.is_upcoming

    @property
    def can_reschedule(self):
        """Check if appointment can be rescheduled"""
        return self.status == 'Pending' and self.is_upcoming

    def cancel(self):
        """Cancel the appointment"""
        if self.can_cancel:
            self.status = 'Cancelled'
            self.save()
            return True
        return False

    def confirm(self):
        """Confirm the appointment"""
        if self.status == 'Pending':
            self.status = 'Confirmed'
            self.save()
            return True
        return False

    def complete(self):
        """Mark appointment as completed"""
        if self.status == 'Confirmed':
            self.status = 'Completed'
            self.save()
            return True
        return False

    @classmethod
    def get_today_appointments(cls):
        """Get all appointments for today"""
        from datetime import date
        return cls.objects.filter(appointment_date=date.today())

    @classmethod
    def get_upcoming_appointments(cls, days=7):
        """Get upcoming appointments within specified days"""
        from datetime import date, timedelta
        end_date = date.today() + timedelta(days=days)
        return cls.objects.filter(
            appointment_date__range=[date.today(), end_date],
            status__in=['Pending', 'Confirmed']
        ).order_by('appointment_date', 'appointment_time')

    @classmethod
    def get_doctor_schedule(cls, doctor, date):
        """Get doctor's schedule for a specific date"""
        return cls.objects.filter(
            doctor=doctor,
            appointment_date=date
        ).order_by('appointment_time')
