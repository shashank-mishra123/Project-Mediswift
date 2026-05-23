from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='liked_by.count', read_only=True)
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(pk=request.user.pk).exists()
        return False


class DoctorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'user', 'name', 'specialty', 'experience',
            'body_part', 'fees', 'hospital', 'qualification', 'about', 'status'
        ]
