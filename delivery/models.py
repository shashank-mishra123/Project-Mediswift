from django.db import models
from django.conf import settings


class DeliveryBoy(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='delivery_profile', null=True, blank=True
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=20, blank=True)
    service_area = models.TextField(blank=True)
    total_deliveries = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'delivery_boys'
        ordering = ['name']
        verbose_name = 'Delivery Boy'
        verbose_name_plural = 'Delivery Boys'

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def is_available(self):
        """Check if delivery boy is available"""
        return self.status == 'available'

    @property
    def current_deliveries(self):
        """Get current deliveries (out for delivery)"""
        return self.deliveries.filter(status='out_for_delivery').count()

    @property
    def completed_deliveries_today(self):
        """Get completed deliveries today"""
        from datetime import date
        return self.deliveries.filter(
            status='delivered',
            updated_at__date=date.today()
        ).count()

    def set_available(self):
        """Set status to available"""
        self.status = 'available'
        self.save()

    def set_busy(self):
        """Set status to busy"""
        self.status = 'busy'
        self.save()

    def set_offline(self):
        """Set status to offline"""
        self.status = 'offline'
        self.save()

    def assign_order(self, order):
        """Assign an order to this delivery boy"""
        if self.is_available and order.status == 'confirmed':
            order.delivery_boy = self
            order.status = 'out_for_delivery'
            order.save()
            self.status = 'busy'
            self.save()
            return True
        return False

    def complete_delivery(self, order):
        """Complete a delivery"""
        if order.delivery_boy == self and order.status == 'out_for_delivery':
            order.status = 'delivered'
            order.payment_status = 'paid'
            order.save()
            self.total_deliveries += 1
            self.status = 'available'
            self.save()
            return True
        return False

    @classmethod
    def get_available_boys(cls):
        """Get all available delivery boys"""
        return cls.objects.filter(status='available')

    @classmethod
    def get_top_performers(cls, limit=10):
        """Get top performing delivery boys by total deliveries"""
        return cls.objects.filter(
            status__in=['available', 'busy']
        ).order_by('-total_deliveries')[:limit]
