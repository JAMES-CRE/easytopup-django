from rest_framework import serializers
from .models import Station

class StationSerializer(serializers.ModelSerializer):
    cylinder_prices = serializers.SerializerMethodField()
    pending = serializers.SerializerMethodField()

    class Meta:
        model = Station
        fields = '__all__'
        read_only_fields = ['id', 'created_at']  # Make id read-only

    def get_cylinder_prices(self, obj):
        return obj.cylinder_prices

    def get_pending(self, obj):
        return not obj.verified