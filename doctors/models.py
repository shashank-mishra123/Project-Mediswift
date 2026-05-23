from django.db import models
from django.conf import settings


class Doctor(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='doctor_profile', null=True, blank=True
    )
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    experience = models.IntegerField(default=0)
    body_part = models.CharField(max_length=50, blank=True)
    fees = models.IntegerField(default=500)
    hospital = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    about = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='liked_doctors',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctors'
        ordering = ['name']

    def __str__(self):
        return f"Dr. {self.name} — {self.specialty}"

    @property
    def full_name(self):
        return f"Dr. {self.name}"

    @property
    def total_appointments(self):
        """Total appointments for this doctor"""
        return self.appointments.count()

    @property
    def pending_appointments(self):
        """Pending appointments count"""
        return self.appointments.filter(status='Pending').count()

    @property
    def completed_appointments(self):
        """Completed appointments count"""
        return self.appointments.filter(status='Completed').count()

    @property
    def likes_count(self):
        """Number of patients who liked this doctor"""
        return self.liked_by.count()

    @property
    def is_available(self):
        """Check if doctor is available"""
        return self.status == 'active'

    @property
    def experience_display(self):
        """Display experience in readable format"""
        if self.experience == 1:
            return "1 year"
        return f"{self.experience} years"

    def get_upcoming_appointments(self, limit=5):
        """Get upcoming appointments for this doctor"""
        from django.utils import timezone
        from appointments.models import Appointment
        today = timezone.now().date()
        return Appointment.objects.filter(
            doctor=self,
            appointment_date__gte=today,
            status__in=['Pending', 'Confirmed']
        ).order_by('appointment_date', 'appointment_time')[:limit]

    def get_today_appointments(self):
        """Get today's appointments"""
        from django.utils import timezone
        from appointments.models import Appointment
        today = timezone.now().date()
        return Appointment.objects.filter(
            doctor=self,
            appointment_date=today
        ).order_by('appointment_time')

    def get_monthly_stats(self, year=None, month=None):
        """Get monthly statistics for the doctor"""
        from django.utils import timezone
        from django.db.models import Count
        import calendar

        if not year or not month:
            now = timezone.now()
            year = now.year
            month = now.month

        _, last_day = calendar.monthrange(year, month)

        appointments = self.appointments.filter(
            created_at__year=year,
            created_at__month=month
        )

        return {
            'total_appointments': appointments.count(),
            'completed': appointments.filter(status='Completed').count(),
            'cancelled': appointments.filter(status='Cancelled').count(),
            'pending': appointments.filter(status='Pending').count(),
            'confirmed': appointments.filter(status='Confirmed').count(),
        }
