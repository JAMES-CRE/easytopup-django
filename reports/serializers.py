from rest_framework import serializers
from .models import Report, Review

class ReportSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    station_name = serializers.SerializerMethodField()

    #  REPLY FIELDS
    replied_by_name = serializers.SerializerMethodField()
    has_reply = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'user']

    def get_user_name(self, obj):
        return obj.user.email if obj.user else None

    def get_station_name(self, obj):
        return obj.station.name if obj.station else None

    # NEW REPLY METHODS
    def get_replied_by_name(self, obj):
        """Get the name of the person who replied"""
        if obj.replied_by:
            if obj.replied_by.first_name or obj.replied_by.last_name:
                return f"{obj.replied_by.first_name} {obj.replied_by.last_name}".strip()
            return obj.replied_by.email
        return None

    def get_has_reply(self, obj):
        """Check if a reply exists"""
        return obj.operator_reply is not None and obj.operator_reply != ''


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