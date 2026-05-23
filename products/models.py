from django.conf import settings
from django.db import models
from django.db.models import Count


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.display_name or self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    subcategory = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(default=100)
    prescription_required = models.BooleanField(default=False)
    discount_percent = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.5)
    total_ratings = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='liked_products',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        if self.discount_percent:
            return float(self.price) * (1 - self.discount_percent / 100)
        return float(self.price)

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0

    @property
    def stock_status(self):
        """Get stock status"""
        if self.stock == 0:
            return "Out of Stock"
        elif self.stock < 10:
            return "Low Stock"
        return "In Stock"

    @property
    def likes_count(self):
        """Number of users who liked this product"""
        return self.liked_by.count()

    @property
    def is_near_expiry(self):
        """Check if product is near expiry (within 90 days)"""
        from datetime import date, timedelta
        if not self.expiry_date:
            return False
        return self.expiry_date <= date.today() + timedelta(days=90)

    @property
    def days_to_expiry(self):
        """Days until expiry"""
        from datetime import date
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days

    def reduce_stock(self, quantity):
        """Reduce stock by given quantity"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def increase_stock(self, quantity):
        """Increase stock by given quantity"""
        self.stock += quantity
        self.save()

    def get_similar_products(self, limit=5):
        """Get similar products based on category"""
        return Product.objects.filter(
            category=self.category,
            is_active=True
        ).exclude(pk=self.pk)[:limit]

    def get_popular_products(limit=10):
        """Class method to get most liked products"""
        return Product.objects.filter(
            is_active=True
        ).annotate(
            likes_count=Count('liked_by')
        ).order_by('-likes_count')[:limit]

    def get_low_stock_products(threshold=10):
        """Class method to get products with low stock"""
        return Product.objects.filter(
            stock__lte=threshold,
            is_active=True
        ).order_by('stock')

    def get_near_expiry_products(days=90):
        """Class method to get products near expiry"""
        from datetime import date, timedelta
        cutoff_date = date.today() + timedelta(days=days)
        return Product.objects.filter(
            expiry_date__lte=cutoff_date,
            expiry_date__gte=date.today(),
            is_active=True
        ).order_by('expiry_date')
