from rest_framework import serializers
from .models import Station


class StationSerializer(serializers.ModelSerializer):
    """
    Main serializer for Station model.
    Handles both read and write operations.
    """

    # PENDING: true when not verified
    pending = serializers.SerializerMethodField()

    # FLUTTER FIELD MAPPING
    # These accept data from Flutter and map to backend fields
    petrol = serializers.JSONField(required=False, allow_null=True, write_only=True)
    diesel = serializers.JSONField(required=False, allow_null=True, write_only=True)
    charging_points = serializers.JSONField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Station
        fields = [
            'id',
            'name',
            'type',
            'lat',
            'lng',
            'status',
            'price',
            'phone',
            'whatsapp',
            'has_backup_generator',
            'lpg_type',
            'delivery_available',
            'photos',
            'verified',
            'pending',
            'created_at',
            'operator',
            # ─── Flutter-friendly fields ───
            'petrol',
            'diesel',
            'charging_points',
        ]
        read_only_fields = ['id', 'created_at', 'verified', 'operator', 'pending']

    def get_pending(self, obj):
        return not obj.verified

    # READ: Django to Flutter
    def to_representation(self, instance):
        """When sending data to Flutter (READ)"""
        representation = super().to_representation(instance)


        representation['petrol'] = instance.petrol_data or None


        representation['diesel'] = instance.diesel_data or None


        representation['charging_points'] = instance.ev_data or []

        return representation

    #  CREATE: Flutter to Django
    def create(self, validated_data):
        """Handle creation with premium data"""
        # Extract Flutter fields
        petrol_data = validated_data.pop('petrol', None)
        diesel_data = validated_data.pop('diesel', None)
        ev_data = validated_data.pop('charging_points', None)

        # Create station
        station = Station.objects.create(**validated_data)

        # Set premium data
        if petrol_data is not None:
            station.petrol_data = petrol_data
        if diesel_data is not None:
            station.diesel_data = diesel_data
        if ev_data is not None:
            station.ev_data = ev_data

        station.save()
        return station

    # UPDATE: Flutter to Django
    def update(self, instance, validated_data):
        """Handle updates with premium data"""
        # Extract Flutter fields
        petrol_data = validated_data.pop('petrol', None)
        diesel_data = validated_data.pop('diesel', None)
        ev_data = validated_data.pop('charging_points', None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update premium data (even if empty, to clear)
        if petrol_data is not None:
            instance.petrol_data = petrol_data
        if diesel_data is not None:
            instance.diesel_data = diesel_data
        if ev_data is not None:
            instance.ev_data = ev_data

        instance.save()
        return instance