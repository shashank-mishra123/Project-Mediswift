from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('appointments/booked-slots/', views.BookedSlotsView.as_view(), name='booked-slots'),

    # Patient
    path('appointments/', views.BookAppointmentView.as_view(), name='book-appointment'),
    path('appointments/my/', views.MyAppointmentsView.as_view(), name='my-appointments'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<int:pk>/cancel/', views.CancelAppointmentView.as_view(), name='cancel-appointment'),

    # Doctor
    path('doctor/appointments/', views.DoctorAppointmentsView.as_view(), name='doctor-appointments'),
    path('doctor/appointments/<int:pk>/status/', views.DoctorUpdateAppointmentView.as_view(), name='doctor-update-appointment'),

    # Admin
    path('admin/appointments/', views.AdminAppointmentListView.as_view(), name='admin-appointments'),
    path('admin/appointments/<int:pk>/', views.AdminAppointmentDetailView.as_view(), name='admin-appointment-detail'),
]
