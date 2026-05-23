from django.urls import path
from . import views

urlpatterns = [
    # Delivery boy own endpoints
    path('delivery/my-profile/', views.MyDeliveryProfileView.as_view(), name='delivery-my-profile'),
    path('delivery/my-orders/', views.MyAssignedOrdersView.as_view(), name='delivery-my-orders'),
    path('delivery/my-status/', views.UpdateDeliveryStatusView.as_view(), name='delivery-my-status'),
    path('delivery/orders/<int:pk>/delivered/', views.MarkOrderDeliveredView.as_view(), name='delivery-mark-delivered'),
    path('delivery/dashboard/', views.DeliveryDashboardView.as_view(), name='delivery-dashboard'),

    # Admin endpoints
    path('admin/delivery/', views.AdminDeliveryListCreateView.as_view(), name='admin-delivery-list'),
    path('admin/delivery/available/', views.AdminAvailableDeliveryBoysView.as_view(), name='admin-delivery-available'),
    path('admin/delivery/<int:pk>/', views.AdminDeliveryDetailView.as_view(), name='admin-delivery-detail'),
]
