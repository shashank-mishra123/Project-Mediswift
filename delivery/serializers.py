from rest_framework import serializers
from .models import DeliveryBoy


class DeliveryBoySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoy
        fields = '__all__'
        read_only_fields = ['id', 'total_deliveries', 'rating', 'created_at', 'updated_at']


class DeliveryBoyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoy
        fields = ['user', 'name', 'phone', 'vehicle_number', 'service_area', 'status']


class DeliveryStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['available', 'busy', 'offline'])
