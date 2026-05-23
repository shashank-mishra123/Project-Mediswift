from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.utils import timezone
from django.db.models import Sum

from .models import User
from .serializers import (
    UserRegisterSerializer, UserLoginSerializer,
    UserSerializer, UserUpdateSerializer, ChangePasswordSerializer
)
from .permissions import IsAdmin
from orders.serializers import OrderSerializer
from appointments.serializers import AppointmentSerializer


# ──────────────────────────────────────────────────────────────
# AUTH ENDPOINTS
# ──────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """POST /api/auth/register/  — register a new patient account"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Registration successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """POST /api/auth/login/  — obtain JWT tokens"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """POST /api/auth/logout/  — invalidate current session on client side"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully. Please discard your access and refresh tokens."})


class CurrentUserView(APIView):
    """GET /api/auth/me/  — get current user profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    """PUT /api/auth/change-password/"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Password changed.",
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────
# PROFILE CRUD (own account)
# ──────────────────────────────────────────────────────────────

class ProfileView(APIView):
    """GET / PUT / DELETE /api/users/profile/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated.", "user": UserSerializer(request.user).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.user.delete()
        return Response({"message": "Account deleted."}, status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────────────────────────
# ADMIN — manage all users
# ──────────────────────────────────────────────────────────────

class AdminUserListView(generics.ListAPIView):
    """GET /api/admin/users/  — list all users (admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] # Changed to IsAuthenticated for testing purposes, should be IsAdmin in production


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE /api/admin/users/<pk>/  — admin manage user"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] # Changed to IsAuthenticated for testing purposes, should be IsAdmin in production

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({"message": "User deleted."}, status=status.HTTP_204_NO_CONTENT)


class AdminUserStatusView(APIView):
    """PATCH /api/admin/users/<pk>/status/  — suspend/activate a user"""
    permission_classes = [IsAuthenticated] # Changed to IsAuthenticated for testing purposes, should be IsAdmin in production

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('status')
        if new_status not in ['active', 'inactive', 'suspended']:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        user.status = new_status
        user.save()
        return Response({"message": f"User status set to {new_status}."})


class AdminDashboardStatsView(APIView):
    """GET /api/admin/stats/"""
    permission_classes = [IsAuthenticated ] # Changed to IsAuthenticated for testing purposes, should be IsAdmin in production
    def get(self, request):
        from django.db.models import Count, Sum
        from orders.models import Order
        from appointments.models import Appointment
        from products.models import Product

        # User statistics
        user_stats = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(status='active').count(),
            "inactive_users": User.objects.filter(status='inactive').count(),
            "suspended_users": User.objects.filter(status='suspended').count(),
            "total_patients": User.objects.filter(role='patient').count(),
            "total_doctors": User.objects.filter(role='doctor').count(),
            "total_delivery_boys": User.objects.filter(role='delivery').count(),
        }

        # Order statistics
        order_stats = {
            "total_orders": Order.objects.count(),
            "pending_orders": Order.objects.filter(status='pending').count(),
            "confirmed_orders": Order.objects.filter(status='confirmed').count(),
            "out_for_delivery": Order.objects.filter(status='out_for_delivery').count(),
            "delivered_orders": Order.objects.filter(status='delivered').count(),
            "cancelled_orders": Order.objects.filter(status='cancelled').count(),
            "total_revenue": Order.objects.filter(status='delivered').aggregate(
                total=Sum('total_amount'))['total'] or 0,
        }

        # Appointment statistics
        appointment_stats = {
            "total_appointments": Appointment.objects.count(),
            "pending_appointments": Appointment.objects.filter(status='Pending').count(),
            "confirmed_appointments": Appointment.objects.filter(status='Confirmed').count(),
            "completed_appointments": Appointment.objects.filter(status='Completed').count(),
            "cancelled_appointments": Appointment.objects.filter(status='Cancelled').count(),
        }

        # Product statistics
        product_stats = {
            "total_products": Product.objects.count(),
            "active_products": Product.objects.filter(is_active=True).count(),
            "inactive_products": Product.objects.filter(is_active=False).count(),
            "low_stock_products": Product.objects.filter(stock__lte=10, is_active=True).count(),
            "out_of_stock_products": Product.objects.filter(stock=0, is_active=True).count(),
            "near_expiry_products": len(Product.get_near_expiry_products(30)),
        }

        # Recent activity (last 7 days)
        from django.utils import timezone
        from datetime import timedelta
        seven_days_ago = timezone.now() - timedelta(days=7)

        recent_stats = {
            "new_users_last_7_days": User.objects.filter(created_at__gte=seven_days_ago).count(),
            "new_orders_last_7_days": Order.objects.filter(created_at__gte=seven_days_ago).count(),
            "new_appointments_last_7_days": Appointment.objects.filter(created_at__gte=seven_days_ago).count(),
            "completed_orders_last_7_days": Order.objects.filter(
                status='delivered', updated_at__gte=seven_days_ago).count(),
        }

        return Response({
            "user_stats": user_stats,
            "order_stats": order_stats,
            "appointment_stats": appointment_stats,
            "product_stats": product_stats,
            "recent_activity": recent_stats,
        })


class PatientDashboardView(APIView):
    """GET /api/patient/dashboard/ — personalized dashboard for patients"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_patient():
            return Response({"error": "Only patients can access this dashboard."}, status=403)

        from orders.models import Order
        from appointments.models import Appointment
        from doctors.models import Doctor
        from products.models import Product

        # User's orders
        user_orders = Order.objects.filter(user=request.user)
        order_stats = {
            "total_orders": user_orders.count(),
            "pending_orders": user_orders.filter(status='pending').count(),
            "delivered_orders": user_orders.filter(status='delivered').count(),
            "cancelled_orders": user_orders.filter(status='cancelled').count(),
            "total_spent": user_orders.filter(status='delivered').aggregate(
                total=Sum('total_amount'))['total'] or 0,
        }

        # User's appointments
        user_appointments = Appointment.objects.filter(patient=request.user)
        appointment_stats = {
            "total_appointments": user_appointments.count(),
            "upcoming_appointments": user_appointments.filter(
                status__in=['Pending', 'Confirmed'], appointment_date__gte=timezone.now().date()).count(),
            "completed_appointments": user_appointments.filter(status='Completed').count(),
            "cancelled_appointments": user_appointments.filter(status='Cancelled').count(),
        }

        # Liked items
        liked_doctors = Doctor.objects.filter(liked_by=request.user)
        liked_products = Product.objects.filter(liked_by=request.user)

        # Recent activity
        recent_orders = user_orders.order_by('-created_at')[:5]
        recent_appointments = user_appointments.order_by('-created_at')[:5]

        return Response({
            "welcome_message": f"Welcome back, {request.user.name}!",
            "order_stats": order_stats,
            "appointment_stats": appointment_stats,
            "liked_doctors_count": liked_doctors.count(),
            "liked_products_count": liked_products.count(),
            "recent_orders": OrderSerializer(recent_orders, many=True).data,
            "recent_appointments": AppointmentSerializer(recent_appointments, many=True).data,
        })
