from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Allow only admin users (safe + production-ready)"""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.is_staff or
                request.user.is_superuser or
                getattr(request.user, 'role', '').lower() == 'admin'
            )
        )

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, 'role', '').lower() == 'doctor'
        )


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, 'role', '').lower() == 'patient'
        )


class IsDelivery(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, 'role', '').lower() == 'delivery'
        )


class IsAdminOrDoctor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, 'role', '').lower() in ['admin', 'doctor']
        )


class IsAdminOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            getattr(request.user, 'role', '').lower() == 'admin'
            or obj == request.user
        )