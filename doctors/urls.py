from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('doctors/', views.PublicDoctorListView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>/', views.PublicDoctorDetailView.as_view(), name='doctor-detail'),
    path('doctors/<int:pk>/like/', views.DoctorLikeToggleView.as_view(), name='doctor-like'),
    path('doctors/<int:pk>/likes/', views.DoctorLikesView.as_view(), name='doctor-likes'),

    # Doctor own profile
    path('doctors/my-profile/', views.DoctorProfileView.as_view(), name='doctor-my-profile'),
    path('doctor/dashboard/', views.DoctorDashboardView.as_view(), name='doctor-dashboard'),

    # Admin
    path('admin/doctors/', views.AdminDoctorListCreateView.as_view(), name='admin-doctor-list'),
    path('admin/doctors/<int:pk>/', views.AdminDoctorDetailView.as_view(), name='admin-doctor-detail'),
    path('admin/doctors/<int:pk>/status/', views.AdminDoctorStatusView.as_view(), name='admin-doctor-status'),
]
