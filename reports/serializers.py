from rest_framework import serializers
from .models import Report

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