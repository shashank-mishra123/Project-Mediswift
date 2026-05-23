from rest_framework import serializers
from .models import Category, Product
import datetime


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'display_name', 'icon', 'product_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    discounted_price = serializers.ReadOnlyField()
    likes_count = serializers.IntegerField(source='liked_by.count', read_only=True)
    liked_by_user = serializers.SerializerMethodField()
    days_to_expiry = serializers.SerializerMethodField()
    near_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(pk=request.user.pk).exists()
        return False

    def get_days_to_expiry(self, obj):
        if obj.expiry_date:
            return (obj.expiry_date - datetime.date.today()).days
        return None

    def get_near_expiry(self, obj):
        days = self.get_days_to_expiry(obj)
        return days is not None and days < 90


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'price', 'category', 'subcategory', 'description',
            'image_url', 'expiry_date', 'manufacturer', 'stock',
            'prescription_required', 'discount_percent', 'is_active'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value
