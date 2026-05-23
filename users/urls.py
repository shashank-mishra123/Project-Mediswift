from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),

    # ── Own profile ───────────────────────────────────────────
    path('users/profile/', views.ProfileView.as_view(), name='profile'),
    path('patient/dashboard/', views.PatientDashboardView.as_view(), name='patient-dashboard'),

    # ── Admin user management ─────────────────────────────────
    path('admin/users/', views.AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<int:pk>/status/', views.AdminUserStatusView.as_view(), name='admin-user-status'),
    path('admin/stats/', views.AdminDashboardStatsView.as_view(), name='admin-stats'),
]
