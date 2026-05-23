from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import DeliveryBoy
from .serializers import DeliveryBoySerializer, DeliveryBoyCreateSerializer, DeliveryStatusSerializer
from users.permissions import IsAdmin, IsDelivery
from orders.models import Order
from orders.serializers import OrderSerializer


# ──────────────────────────────────────────────────────────────
# DELIVERY BOY — own profile & assigned orders
# ──────────────────────────────────────────────────────────────

class MyDeliveryProfileView(APIView):
    """GET / PUT  /api/delivery/my-profile/"""
    permission_classes = [IsDelivery]

    def get(self, request):
        try:
            profile = DeliveryBoy.objects.get(user=request.user)
            return Response(DeliveryBoySerializer(profile).data)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Delivery profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = DeliveryBoy.objects.get(user=request.user)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Delivery profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeliveryBoyCreateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated.", "profile": DeliveryBoySerializer(profile).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyAssignedOrdersView(APIView):
    """GET /api/delivery/my-orders/  — orders assigned to this delivery boy"""
    permission_classes = [IsDelivery]

    def get(self, request):
        try:
            profile = DeliveryBoy.objects.get(user=request.user)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Delivery profile not found."}, status=status.HTTP_404_NOT_FOUND)
        orders = Order.objects.filter(delivery_boy=profile).prefetch_related('items')
        return Response(OrderSerializer(orders, many=True).data)


class UpdateDeliveryStatusView(APIView):
    """PATCH /api/delivery/my-status/  — delivery boy sets availability"""
    permission_classes = [IsDelivery]

    def patch(self, request):
        try:
            profile = DeliveryBoy.objects.get(user=request.user)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Delivery profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeliveryStatusSerializer(data=request.data)
        if serializer.is_valid():
            profile.status = serializer.validated_data['status']
            profile.save()
            return Response({"message": f"Status updated to {profile.status}."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarkOrderDeliveredView(APIView):
    """PATCH /api/delivery/orders/<pk>/delivered/"""
    permission_classes = [IsDelivery]

    def patch(self, request, pk):
        try:
            profile = DeliveryBoy.objects.get(user=request.user)
            order = Order.objects.get(pk=pk, delivery_boy=profile)
        except (DeliveryBoy.DoesNotExist, Order.DoesNotExist):
            return Response({"error": "Order not found or not assigned to you."}, status=status.HTTP_404_NOT_FOUND)
        if order.status != 'out_for_delivery':
            return Response({"error": "Order is not out for delivery."}, status=400)
        order.status = 'delivered'
        order.payment_status = 'paid'
        order.save()
        profile.total_deliveries += 1
        profile.status = 'available'
        profile.save()
        return Response({"message": "Order marked as delivered.", "order": OrderSerializer(order).data})


# ──────────────────────────────────────────────────────────────
# ADMIN — manage delivery boys
# ──────────────────────────────────────────────────────────────

class AdminDeliveryListCreateView(generics.ListCreateAPIView):
    """GET / POST /api/admin/delivery/"""
    queryset = DeliveryBoy.objects.all()
    serializer_class = DeliveryBoySerializer
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = DeliveryBoyCreateSerializer(data=request.data)
        if serializer.is_valid():
            delivery_boy = serializer.save()
            return Response(
                {"message": "Delivery boy created.", "delivery_boy": DeliveryBoySerializer(delivery_boy).data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminDeliveryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE /api/admin/delivery/<pk>/"""
    queryset = DeliveryBoy.objects.all()
    serializer_class = DeliveryBoySerializer
    permission_classes = [IsAdmin]

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"message": "Delivery boy deleted."}, status=status.HTTP_204_NO_CONTENT)


class AdminAvailableDeliveryBoysView(APIView):
    """GET /api/admin/delivery/available/  — get delivery boys who are free"""
    permission_classes = [IsAdmin]

    def get(self, request):
        boys = DeliveryBoy.objects.filter(status='available')
        return Response({
            "count": boys.count(),
            "delivery_boys": DeliveryBoySerializer(boys, many=True).data
        })


class DeliveryDashboardView(APIView):
    """GET /api/delivery/dashboard/ — personalized dashboard for delivery boys"""
    permission_classes = [IsDelivery]

    def get(self, request):
        try:
            profile = DeliveryBoy.objects.get(user=request.user)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Delivery profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Current assignments
        current_orders = Order.objects.filter(
            delivery_boy=profile,
            status='out_for_delivery'
        ).prefetch_related('items')

        # Today's deliveries
        from datetime import date
        today_deliveries = profile.deliveries.filter(
            status='delivered',
            updated_at__date=date.today()
        ).count()

        # Performance stats
        performance_stats = {
            "total_deliveries": profile.total_deliveries,
            "rating": profile.rating,
            "status": profile.status,
            "today_deliveries": today_deliveries,
            "current_assignments": current_orders.count(),
        }

        # Recent deliveries
        recent_deliveries = Order.objects.filter(
            delivery_boy=profile,
            status='delivered'
        ).order_by('-updated_at')[:10]

        return Response({
            "welcome_message": f"Good day, {profile.name}!",
            "performance_stats": performance_stats,
            "current_orders": OrderSerializer(current_orders, many=True).data,
            "recent_deliveries": OrderSerializer(recent_deliveries, many=True).data,
        })
