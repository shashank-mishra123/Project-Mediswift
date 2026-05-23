from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
        ('delivery', 'Delivery'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    joined = models.DateField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.split()[0] if self.name else self.email

    def is_patient(self):
        return self.role == 'patient'

    def is_doctor(self):
        return self.role == 'doctor'

    def is_admin(self):
        return self.role == 'admin'

    def is_delivery_boy(self):
        return self.role == 'delivery'

    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def activate(self):
        """Custom method to activate user"""
        self.status = 'active'
        self.save()

    def deactivate(self):
        """Custom method to deactivate user"""
        self.status = 'inactive'
        self.save()

    def suspend(self):
        """Custom method to suspend user"""
        self.status = 'suspended'
        self.save()

    @property
    def is_active_user(self):
        """Property to check if user is active"""
        return self.status == 'active' and self.is_active

    @property
    def total_orders(self):
        """Property to get total orders for patients"""
        if self.is_patient():
            return self.orders.count()
        return 0

    @property
    def total_appointments(self):
        """Property to get total appointments for patients"""
        if self.is_patient():
            return self.appointments.count()
        return 0

    @property
    def liked_doctors_count(self):
        """Property to get count of liked doctors"""
        if self.is_patient():
            return self.liked_doctors.count()
        return 0

    @property
    def liked_products_count(self):
        """Property to get count of liked products"""
        if self.is_patient():
            return self.liked_products.count()
        return 0
