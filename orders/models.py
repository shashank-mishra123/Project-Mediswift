from django.db import models
from django.conf import settings
import random, datetime


def gen_order_number():
    return f"ORD{datetime.datetime.now().strftime('%y%m%d')}{random.randint(10000,99999)}"


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='cart_items', null=True, blank=True
    )
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart'
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} — {self.product.name} x{self.quantity}"

    @property
    def subtotal(self):
        return float(self.product.price) * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='orders'
    )
    order_number = models.CharField(max_length=50, unique=True, default=gen_order_number)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    delivery_boy = models.ForeignKey(
        'delivery.DeliveryBoy', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='deliveries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number

    @property
    def items_count(self):
        """Total number of items in the order"""
        return self.items.count()

    @property
    def total_quantity(self):
        """Total quantity of all items"""
        return sum(item.quantity for item in self.items.all())

    @property
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']

    @property
    def can_ship(self):
        """Check if order can be shipped"""
        return self.status == 'confirmed'

    @property
    def is_delivered(self):
        """Check if order is delivered"""
        return self.status == 'delivered'

    def cancel(self):
        """Cancel the order and restore stock"""
        if self.can_cancel:
            # Restore stock for all items
            for item in self.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()
            self.status = 'cancelled'
            self.save()
            return True
        return False

    def confirm(self):
        """Confirm the order"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.save()
            return True
        return False

    def ship(self, delivery_boy=None):
        """Mark order as out for delivery"""
        if self.can_ship:
            self.status = 'out_for_delivery'
            if delivery_boy:
                self.delivery_boy = delivery_boy
            self.save()
            return True
        return False

    def deliver(self):
        """Mark order as delivered"""
        if self.status == 'out_for_delivery':
            self.status = 'delivered'
            self.payment_status = 'paid'
            self.save()
            return True
        return False

    @classmethod
    def get_pending_orders(cls):
        """Get all pending orders"""
        return cls.objects.filter(status='pending')

    @classmethod
    def get_orders_by_status(cls, status):
        """Get orders by status"""
        return cls.objects.filter(status=status)

    @classmethod
    def get_monthly_revenue(cls, year=None, month=None):
        """Get monthly revenue"""
        from django.utils import timezone
        from django.db.models import Sum

        if not year or not month:
            now = timezone.now()
            year = now.year
            month = now.month

        return cls.objects.filter(
            status='delivered',
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=Sum('total_amount'))['total'] or 0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.order.order_number} — {self.product.name} x{self.quantity}"

    @property
    def subtotal(self):
        return float(self.price) * self.quantity
