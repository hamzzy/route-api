import hashlib
import logging
from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import RouteRequestSerializer, RouteResponseSerializer
from .services.routing import RoutePlanningService
from .services.hybrid_fuel_optimization import HybridFuelOptimizationService
from .services.geocoding import GeocodingService
from .utils import polyline_to_geojson

logger = logging.getLogger(__name__)


class RoutePlanView(APIView):
    """
    API endpoint for route planning with optimal fuel stops
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Plan a route with optimal fuel stops
        """
        # Validate input using serializer
        serializer = RouteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid input data', 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start = serializer.validated_data['start']
        finish = serializer.validated_data['finish']
        
        # Create cache key
        cache_key = f"route_plan:{hashlib.md5(f'{start}:{finish}'.encode()).hexdigest()}"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached result for route {start} -> {finish}")
            return Response(cached_result)
        
        try:
            # Initialize services
            routing_service = RoutePlanningService()
            fuel_service = HybridFuelOptimizationService()
            
            # Plan the route
            route_data = routing_service.plan_route_sync(start, finish)
            
            if not route_data:
                logger.warning(f"Could not plan route from {start} to {finish}")
                return Response(
                    {'error': 'Could not plan route between the specified locations'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract route information
            start_coords = route_data['start_coords']
            end_coords = route_data['end_coords']
            route = route_data['route']
            
            # Convert route geometry to points for fuel optimization
            # For now, we'll use start and end points and interpolate
            # In a real implementation, you'd decode the polyline
            route_points = [start_coords, end_coords]
            
            # Get states along the route (simplified - in reality you'd parse the route)
            # For now, we'll get stations in all states
            states = None
            
            # Optimize fuel stops
            fuel_optimization = fuel_service.find_optimal_fuel_stops(
                start_coords, end_coords
            )
            
            # Prepare fuel stops for response
            fuel_stops_response = []
            for stop in fuel_optimization['fuel_stops']:
                station = stop['station']
                fuel_stops_response.append({
                    'name': station.name,
                    'address': station.address,
                    'city': station.city,
                    'state': station.state,
                    'coordinates': {
                        'lat': station.latitude,
                        'lon': station.longitude
                    },
                    'price_per_gallon': float(station.retail_price),
                            'distance_from_prev_miles': round(stop['distance_from_previous'], 2),
                    'fuel_needed_gallons': round(stop['fuel_needed'], 2),
                    'cost': round(stop['cost'], 2)
                })
            
            # Prepare response
            response_data = {
                'summary': {
                    'start': {
                        'location': start,
                        'coordinates': {
                            'lat': start_coords[0],
                            'lon': start_coords[1]
                        }
                    },
                    'finish': {
                        'location': finish,
                        'coordinates': {
                            'lat': end_coords[0],
                            'lon': end_coords[1]
                        }
                    },
                    'total_distance_miles': round(route['distance'] / 1609.34, 2),  # Convert meters to miles
                    'total_duration_hours': round(route['duration'] / 3600, 2),  # Convert seconds to hours
                    'fuel_efficiency_mpg': settings.VEHICLE_MPG,
                    'vehicle_max_range_miles': settings.VEHICLE_MAX_RANGE,
                    'total_cost': fuel_optimization['summary']['total_cost'],
                    'total_fuel_gallons': fuel_optimization['summary']['total_fuel_gallons'],
                    'number_of_stops': fuel_optimization['summary']['number_of_stops']
                },
                'route': {
                    'geojson': polyline_to_geojson(route['geometry']),
                    'distance_meters': route['distance'],
                    'duration_seconds': route['duration']
                },
                'fuel_stops': fuel_stops_response
            }
            
            # Response data is ready - no need for validation since we control the format
            
            # Cache the result
            cache.set(cache_key, response_data, settings.CACHE_TTL)
            logger.info(f"Successfully planned route from {start} to {finish}")
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error planning route from {start} to {finish}", exc_info=True)
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
