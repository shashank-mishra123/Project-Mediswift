from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Cart, Order, OrderItem
from .serializers import (
    CartSerializer, CartAddSerializer,
    OrderSerializer, OrderCreateSerializer, OrderStatusSerializer
)
from products.models import Product
from users.permissions import IsAdmin


# ──────────────────────────────────────────────────────────────
# CART CRUD
# ──────────────────────────────────────────────────────────────

class CartListView(APIView):
    """GET /api/cart/  — view cart"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user).select_related('product')
        serializer = CartSerializer(items, many=True)
        total = sum(item.subtotal for item in items)
        return Response({
            "items": serializer.data,
            "total": round(total, 2),
            "item_count": items.count()
        })


class CartAddView(APIView):
    """POST /api/cart/add/  — add or increment item"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if product.stock < quantity:
            return Response({"error": f"Only {product.stock} units available."}, status=400)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({
            "message": "Item added to cart.",
            "cart_item": CartSerializer(cart_item).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CartItemView(APIView):
    """PUT / DELETE /api/cart/<pk>/  — update qty or remove"""
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            item = Cart.objects.get(pk=pk, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        qty = request.data.get('quantity')
        if not qty or int(qty) < 1:
            return Response({"error": "Quantity must be at least 1."}, status=400)
        item.quantity = int(qty)
        item.save()
        return Response({"message": "Quantity updated.", "cart_item": CartSerializer(item).data})

    def delete(self, request, pk):
        try:
            item = Cart.objects.get(pk=pk, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"message": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)


class CartClearView(APIView):
    """DELETE /api/cart/clear/"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Cart cleared."}, status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────────────────────────
# ORDERS — PATIENT
# ──────────────────────────────────────────────────────────────

class PlaceOrderView(APIView):
    """POST /api/orders/  — checkout cart into an order with enhanced validation"""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart_items = Cart.objects.filter(user=request.user).select_related('product')
        if not cart_items.exists():
            return Response({"error": "Your cart is empty."}, status=400)

        # Enhanced stock validation
        insufficient_stock_items = []
        total_amount = 0

        for item in cart_items:
            if item.product.stock < item.quantity:
                insufficient_stock_items.append({
                    "product": item.product.name,
                    "available": item.product.stock,
                    "requested": item.quantity
                })
            else:
                total_amount += item.subtotal

        if insufficient_stock_items:
            return Response({
                "error": "Insufficient stock for some items.",
                "insufficient_stock": insufficient_stock_items
            }, status=400)

        # Check for prescription requirements
        prescription_items = []
        for item in cart_items:
            if item.product.prescription_required:
                prescription_items.append(item.product.name)

        if prescription_items:
            return Response({
                "error": "Prescription required for some items. Please upload prescription or consult a doctor.",
                "prescription_required": prescription_items
            }, status=400)

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            shipping_address=serializer.validated_data['shipping_address'],
            payment_method=serializer.validated_data['payment_method'],
        )

        # Create order items and deduct stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            # Deduct stock
            item.product.stock -= item.quantity
            item.product.save()

        # Clear cart
        cart_items.delete()

        # Send order confirmation (you can add email notification here)
        return Response({
            "message": "Order placed successfully!",
            "order": OrderSerializer(order).data,
            "next_steps": [
                "You will receive an order confirmation email shortly.",
                "Track your order status in 'My Orders' section.",
                "Estimated delivery: 3-5 business days."
            ]
        }, status=status.HTTP_201_CREATED)


class MyOrdersView(generics.ListAPIView):
    """GET /api/orders/my/"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class MyOrderDetailView(generics.RetrieveAPIView):
    """GET /api/orders/<pk>/"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CancelOrderView(APIView):
    """PATCH /api/orders/<pk>/cancel/"""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        if order.status not in ['pending', 'confirmed']:
            return Response({"error": "This order cannot be cancelled."}, status=400)
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        order.status = 'cancelled'
        order.save()
        return Response({"message": "Order cancelled.", "order": OrderSerializer(order).data})


# ──────────────────────────────────────────────────────────────
# ADMIN — full Order management
# ──────────────────────────────────────────────────────────────

class AdminOrderListView(generics.ListAPIView):
    """GET /api/admin/orders/"""
    permission_classes = [IsAdmin]
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = Order.objects.all().prefetch_related('items')
        order_status = self.request.query_params.get('status')
        if order_status:
            qs = qs.filter(status=order_status)
        return qs


class AdminOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE /api/admin/orders/<pk>/"""
    permission_classes = [IsAdmin]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"message": "Order deleted."}, status=status.HTTP_204_NO_CONTENT)


class AdminUpdateOrderStatusView(APIView):
    """PATCH /api/admin/orders/<pk>/status/"""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderStatusSerializer(data=request.data)
        if serializer.is_valid():
            order.status = serializer.validated_data['status']
            delivery_boy_id = serializer.validated_data.get('delivery_boy_id')
            if delivery_boy_id:
                order.delivery_boy_id = delivery_boy_id
            order.save()
            return Response({"message": "Order status updated.", "order": OrderSerializer(order).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminOrderStatsView(APIView):
    """GET /api/admin/orders/stats/"""
    permission_classes = [IsAdmin]

    def get(self, request):
        from django.db.models import Sum
        stats = {
            "total_orders": Order.objects.count(),
            "pending": Order.objects.filter(status='pending').count(),
            "confirmed": Order.objects.filter(status='confirmed').count(),
            "out_for_delivery": Order.objects.filter(status='out_for_delivery').count(),
            "delivered": Order.objects.filter(status='delivered').count(),
            "cancelled": Order.objects.filter(status='cancelled').count(),
            "total_revenue": Order.objects.filter(status='delivered').aggregate(
                total=Sum('total_amount'))['total'] or 0,
        }
        return Response(stats)
