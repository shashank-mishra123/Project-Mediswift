from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('categories/', views.PublicCategoryListView.as_view(), name='category-list'),
    path('products/', views.PublicProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.PublicProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/like/', views.ProductLikeToggleView.as_view(), name='product-like'),
    path('products/<int:pk>/likes/', views.ProductLikesView.as_view(), name='product-likes'),
    path('products/recommendations/', views.ProductRecommendationsView.as_view(), name='product-recommendations'),
    path('products/<int:pk>/similar/', views.SimilarProductsView.as_view(), name='product-similar'),

    # Admin categories
    path('admin/categories/', views.AdminCategoryListCreateView.as_view(), name='admin-category-list'),
    path('admin/categories/<int:pk>/', views.AdminCategoryDetailView.as_view(), name='admin-category-detail'),

    # Admin products
    path('admin/products/', views.AdminProductListCreateView.as_view(), name='admin-product-list'),
    path('admin/products/<int:pk>/', views.AdminProductDetailView.as_view(), name='admin-product-detail'),
    path('admin/products/low-stock/', views.AdminLowStockView.as_view(), name='admin-low-stock'),
    path('admin/products/near-expiry/', views.AdminNearExpiryView.as_view(), name='admin-near-expiry'),
]
