from rest_framework import serializers

from locations.models import Location
from .models import Order, CargoType


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'city_name', 'latitude', 'longitude')
        read_only_fields = fields


class CargoTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoType
        fields = ('id', 'name', 'description')


class OrderReadSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    driver = serializers.PrimaryKeyRelatedField(read_only=True)
    cargo_type = CargoTypeSerializer(read_only=True)
    departure_point = LocationSerializer(read_only=True)
    destination_point = LocationSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'sender',
            'driver',
            'departure_point',
            'destination_point',
            'cargo_type',
            'weight',
            'length',
            'width',
            'height',
            'description',
            'distance_km',
            'estimated_time_hours',
            'total_cost',
            'status',
            'created_at',
            'accepted_at',
            'delivered_at',
            'is_driver_sharing_location',
        )
        read_only_fields = fields


class OrderWriteSerializer(serializers.ModelSerializer):
    cargo_type = serializers.PrimaryKeyRelatedField(
        queryset=CargoType.objects.all(), allow_null=True, required=False
    )
    departure_point = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all()
    )
    destination_point = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all()
    )

    class Meta:
        model = Order
        fields = (
            'cargo_type',
            'departure_point',
            'destination_point',
            'weight',
            'length',
            'width',
            'height',
            'description',
            'distance_km',
            'estimated_time_hours',
            'total_cost',
            'status',
            'driver',
            'is_driver_sharing_location',
            'accepted_at',
            'delivered_at',
        )
        read_only_fields = (
            'accepted_at',
            'delivered_at',
        )
