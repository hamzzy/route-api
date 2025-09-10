from rest_framework import serializers
from .models import FuelStation


class FuelStationSerializer(serializers.ModelSerializer):
    """Serializer for fuel station data in API responses"""
    
    class Meta:
        model = FuelStation
        fields = [
            'id', 'name', 'address', 'city', 'state', 
            'retail_price', 'latitude', 'longitude'
        ]


class RouteRequestSerializer(serializers.Serializer):
    """Serializer for route planning requests"""
    start = serializers.CharField(max_length=255, help_text="Start location (e.g., 'New York, NY' or coordinates)")
    finish = serializers.CharField(max_length=255, help_text="Finish location (e.g., 'Chicago, IL' or coordinates)")
    
    def validate_start(self, value):
        """Validate start location format"""
        if not value or not value.strip():
            raise serializers.ValidationError("Start location cannot be empty")
        return value.strip()
    
    def validate_finish(self, value):
        """Validate finish location format"""
        if not value or not value.strip():
            raise serializers.ValidationError("Finish location cannot be empty")
        return value.strip()


class FuelStopSerializer(serializers.Serializer):
    """Serializer for fuel stop data in API responses"""
    station = FuelStationSerializer()
    distance_from_previous = serializers.FloatField()
    fuel_needed = serializers.FloatField()
    cost = serializers.FloatField()


class RouteSummarySerializer(serializers.Serializer):
    """Serializer for route summary data"""
    start = serializers.DictField()
    finish = serializers.DictField()
    total_distance_miles = serializers.FloatField()
    total_duration_hours = serializers.FloatField()
    fuel_efficiency_mpg = serializers.IntegerField()
    vehicle_max_range_miles = serializers.IntegerField()
    total_cost = serializers.FloatField()
    total_fuel_gallons = serializers.FloatField()
    number_of_stops = serializers.IntegerField()


class RouteResponseSerializer(serializers.Serializer):
    """Serializer for complete route planning response"""
    summary = RouteSummarySerializer()
    route = serializers.DictField()
    fuel_stops = FuelStopSerializer(many=True)
