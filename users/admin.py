from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'role', 'status', 'joined']
    list_filter = ['role', 'status']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('name', 'phone', 'address')}),
        ('Role & Status', {'fields': ('role', 'status')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'name', 'password1', 'password2', 'role')}),
    )
