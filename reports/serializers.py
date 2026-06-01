from rest_framework import serializers
from .models import Report, Review 

class ReportSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    station_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'user']
    
    def get_user_name(self, obj):
        return obj.user.email if obj.user else None
    
    def get_station_name(self, obj):
        return obj.station.name if obj.station else None


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Reviews"""
    user_name = serializers.SerializerMethodField()
    user_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'station', 'user', 'rating', 'comment', 'created_at', 'user_name', 'user_photo']
        read_only_fields = ['id', 'created_at', 'user']
    
    def get_user_name(self, obj):
        """Get user's full name"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
        return "Anonymous"
    
    def get_user_photo(self, obj):
        """Get user's profile photo URL"""
        return obj.user.photo_url if obj.user else None