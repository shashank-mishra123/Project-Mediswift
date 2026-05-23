from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
import datetime

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductCreateUpdateSerializer
from users.permissions import IsAdmin, IsPatient


# ──────────────────────────────────────────────────────────────
# PUBLIC ENDPOINTS
# ──────────────────────────────────────────────────────────────

class PublicCategoryListView(generics.ListAPIView):
    """GET /api/categories/"""
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PublicProductListView(generics.ListAPIView):
    """GET /api/products/  — advanced filtering and search"""
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self):
        from django.db.models import Q, Count

        queryset = Product.objects.filter(is_active=True).select_related('category')

        # Basic filters
        category = self.request.query_params.get('category')
        subcategory = self.request.query_params.get('subcategory')
        search = self.request.query_params.get('search')
        prescription = self.request.query_params.get('prescription_required')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        manufacturer = self.request.query_params.get('manufacturer')
        in_stock = self.request.query_params.get('in_stock')
        discount_only = self.request.query_params.get('discount_only')

        # Advanced filters
        sort_by = self.request.query_params.get('sort_by', 'name')
        sort_order = self.request.query_params.get('sort_order', 'asc')
        rating_min = self.request.query_params.get('rating_min')

        # Apply filters
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if subcategory:
            queryset = queryset.filter(subcategory__icontains=subcategory)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(manufacturer__icontains=search)
            )
        if prescription is not None:
            queryset = queryset.filter(prescription_required=(prescription.lower() == 'true'))
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if manufacturer:
            queryset = queryset.filter(manufacturer__icontains=manufacturer)
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(stock__gt=0)
            else:
                queryset = queryset.filter(stock=0)
        if discount_only is not None and discount_only.lower() == 'true':
            queryset = queryset.filter(discount_percent__gt=0)
        if rating_min:
            queryset = queryset.filter(rating__gte=rating_min)

        # Sorting
        sort_field = sort_by
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'

        # Special sorting cases
        if sort_by == 'popularity':
            queryset = queryset.annotate(likes_count=Count('liked_by')).order_by(f'{"-" if sort_order == "desc" else ""}likes_count')
        elif sort_by == 'price':
            queryset = queryset.order_by(sort_field)
        elif sort_by == 'rating':
            queryset = queryset.order_by(sort_field)
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by(sort_field)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data

        # Add metadata
        response_data['metadata'] = {
            'total_products': queryset.count(),
            'filters_applied': bool(request.query_params),
            'sort_by': request.query_params.get('sort_by', 'name'),
            'sort_order': request.query_params.get('sort_order', 'asc'),
        }

        return Response(response_data)


class PublicProductDetailView(generics.RetrieveAPIView):
    """GET /api/products/<pk>/"""
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {'request': self.request}


# ──────────────────────────────────────────────────────────────
# ADMIN — Category CRUD
# ──────────────────────────────────────────────────────────────

class AdminCategoryListCreateView(generics.ListCreateAPIView):
    """GET / POST /api/admin/categories/"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE /api/admin/categories/<pk>/"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"message": "Category deleted."}, status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────────────────────────
# ADMIN — Product CRUD
# ──────────────────────────────────────────────────────────────

class AdminProductListCreateView(generics.ListCreateAPIView):
    """GET / POST /api/admin/products/"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {"message": "Product created.", "product": ProductSerializer(product).data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE /api/admin/products/<pk>/"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin]

    def get_serializer_context(self):
        return {'request': self.request}

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product updated.", "product": ProductSerializer(product).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"message": "Product deleted."}, status=status.HTTP_204_NO_CONTENT)


class AdminLowStockView(APIView):
    """GET /api/admin/products/low-stock/?threshold=10"""
    permission_classes = [IsAdmin]

    def get(self, request):
        threshold = int(request.query_params.get('threshold', 10))
        products = Product.objects.filter(stock__lte=threshold, is_active=True)
        return Response({
            "threshold": threshold,
            "count": products.count(),
            "products": ProductSerializer(products, many=True).data
        })


class ProductLikeToggleView(APIView):
    """POST /api/products/<pk>/like/ and DELETE /api/products/<pk>/like/"""
    permission_classes = [IsAuthenticated, IsPatient]

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, is_active=True)
        product.liked_by.add(request.user)
        return Response({
            "message": "Product liked.",
            "likes_count": product.liked_by.count(),
            "liked_by_user": True,
        })

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk, is_active=True)
        product.liked_by.remove(request.user)
        return Response({
            "message": "Product unliked.",
            "likes_count": product.liked_by.count(),
            "liked_by_user": False,
        })


class ProductLikesView(APIView):
    """GET /api/products/<pk>/likes/"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, is_active=True)
        return Response({
            "product_id": product.pk,
            "likes_count": product.liked_by.count(),
        })


class ProductRecommendationsView(APIView):
    """GET /api/products/recommendations/ — get personalized recommendations"""
    permission_classes = [AllowAny]

    def get(self, request):
        # Get popular products
        popular_products = Product.get_popular_products(8)

        # Get featured products (high rated with discount)
        featured_products = Product.objects.filter(
            is_active=True,
            rating__gte=4.0,
            discount_percent__gt=0
        ).order_by('-rating')[:6]

        # Get new arrivals
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_arrivals = Product.objects.filter(
            is_active=True,
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:6]

        return Response({
            "popular_products": ProductSerializer(popular_products, many=True).data,
            "featured_products": ProductSerializer(featured_products, many=True).data,
            "new_arrivals": ProductSerializer(new_arrivals, many=True).data,
        })


class SimilarProductsView(APIView):
    """GET /api/products/<pk>/similar/ — get similar products"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, is_active=True)
            similar_products = product.get_similar_products(6)
            return Response({
                "product": ProductSerializer(product).data,
                "similar_products": ProductSerializer(similar_products, many=True).data,
            })
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)


class AdminNearExpiryView(APIView):
    """GET /api/admin/products/near-expiry/?days=90"""
    permission_classes = [IsAdmin]

    def get(self, request):
        days = int(request.query_params.get('days', 90))
        cutoff = datetime.date.today() + datetime.timedelta(days=days)
        products = Product.objects.filter(expiry_date__lte=cutoff, expiry_date__gte=datetime.date.today(), is_active=True)
        return Response({
            "days": days,
            "count": products.count(),
            "products": ProductSerializer(products, many=True, context={'request': request}).data
        })
