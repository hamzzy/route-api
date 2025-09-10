import asyncio
import httpx
import json
import logging
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.core.cache import cache
from .geocoding import GeocodingService
from .base import BaseService

logger = logging.getLogger(__name__)


class RoutePlanningService(BaseService):
    """Service for route planning using OSRM and geocoding"""
    
    def __init__(self):
        super().__init__()
        self.osrm_base_url = settings.OSRM_BASE_URL
        self.geocoding_service = GeocodingService()
        
    async def get_route(self, start_coords: Tuple[float, float], 
                       end_coords: Tuple[float, float]) -> Optional[Dict]:
        """
        Get route from OSRM API
        Returns route data including geometry and distance
        """
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords
        
        # Create cache key
        cache_key = f"route:{start_lat}:{start_lon}:{end_lat}:{end_lon}"
        
        # Check cache first
        cached_result = self.get_from_cache(cache_key)
        if cached_result:
            return cached_result
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.osrm_base_url}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
                response = await client.get(
                    url,
                    params={
                        'overview': 'simplified',
                        'geometries': 'polyline',
                        'steps': 'false'
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                if data.get('code') == 'Ok' and data.get('routes'):
                    route = data['routes'][0]
                    result = {
                        'geometry': route['geometry'],
                        'distance': route['distance'],  # in meters
                        'duration': route['duration'],  # in seconds
                        'legs': route['legs']
                    }
                    
                    # Cache for 1 hour
                    self.set_cache(cache_key, result, settings.CACHE_TTL)
                    return result
                    
        except Exception as e:
            self.log_error("OSRM routing error", e)
            
        return None
    
    async def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Geocode a location string to coordinates
        """
        # Check if it's already coordinates
        if isinstance(location, dict) and 'lat' in location and 'lon' in location:
            return (location['lat'], location['lon'])
        
        # Try to parse as coordinates if it's a string
        if isinstance(location, str):
            try:
                # Check if it's in "lat,lon" format
                if ',' in location:
                    lat, lon = location.split(',')
                    return (float(lat.strip()), float(lon.strip()))
            except ValueError:
                pass
        
        # Geocode the address
        # For now, we'll assume it's a city, state format
        # In a real implementation, you'd parse this more intelligently
        parts = location.split(',')
        if len(parts) >= 2:
            city = parts[0].strip()
            state = parts[1].strip()
            return await self.geocoding_service.geocode_address("", city, state)
        
        return None
    
    async def plan_route(self, start: str, finish: str) -> Optional[Dict]:
        """
        Plan a complete route between start and finish locations
        """
        # Geocode both locations
        start_coords = await self.geocode_location(start)
        end_coords = await self.geocode_location(finish)
        
        if not start_coords or not end_coords:
            return None
            
        # Get route from OSRM
        route_data = await self.get_route(start_coords, end_coords)
        
        if not route_data:
            return None
            
        return {
            'start_coords': start_coords,
            'end_coords': end_coords,
            'route': route_data
        }
    
    def plan_route_sync(self, start: str, finish: str) -> Optional[Dict]:
        """
        Synchronous wrapper for route planning
        """
        return asyncio.run(self.plan_route(start, finish))
