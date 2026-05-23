from rest_framework import serializers
from .models import Cart, Order, OrderItem
from products.serializers import ProductSerializer


class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.CharField(source='product.image_url', read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'quantity', 'subtotal', 'added_at']
        read_only_fields = ['id', 'added_at']


class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    delivery_boy_name = serializers.CharField(source='delivery_boy.name', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=['COD', 'UPI', 'Card', 'NetBanking'], default='COD')


class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['pending', 'confirmed', 'out_for_delivery', 'delivered', 'cancelled'])
    delivery_boy_id = serializers.IntegerField(required=False, allow_null=True)
