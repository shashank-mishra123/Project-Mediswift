from django.urls import path
from . import views

urlpatterns = [
    # Cart
    path('cart/', views.CartListView.as_view(), name='cart-list'),
    path('cart/add/', views.CartAddView.as_view(), name='cart-add'),
    path('cart/clear/', views.CartClearView.as_view(), name='cart-clear'),
    path('cart/<int:pk>/', views.CartItemView.as_view(), name='cart-item'),

    # Patient orders
    path('orders/', views.PlaceOrderView.as_view(), name='place-order'),
    path('orders/my/', views.MyOrdersView.as_view(), name='my-orders'),
    path('orders/<int:pk>/', views.MyOrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/cancel/', views.CancelOrderView.as_view(), name='cancel-order'),

    # Admin orders
    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin-orders'),
    path('admin/orders/stats/', views.AdminOrderStatsView.as_view(), name='admin-order-stats'),
    path('admin/orders/<int:pk>/', views.AdminOrderDetailView.as_view(), name='admin-order-detail'),
    path('admin/orders/<int:pk>/status/', views.AdminUpdateOrderStatusView.as_view(), name='admin-order-status'),
]
