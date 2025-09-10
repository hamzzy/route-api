import asyncio
import httpx
import logging
from typing import List, Tuple, Optional
from django.conf import settings
from django.core.cache import cache
from asgiref.sync import sync_to_async
from planner.models import FuelStation
from .base import BaseService

logger = logging.getLogger(__name__)


class GeocodingService(BaseService):
    """Async geocoding service with caching and rate limiting"""
    
    def __init__(self):
        super().__init__()
        self.base_url = settings.NOMINATIM_BASE_URL
        self.user_agent = settings.NOMINATIM_USER_AGENT
        self.rate_limit_delay = 1.1  # Slightly more than 1 second for rate limiting
        
    async def geocode_address(self, address: str, city: str, state: str) -> Optional[Tuple[float, float]]:
        """
        Geocode an address using Nominatim with caching
        Returns (latitude, longitude) or None if geocoding fails
        """
        # Create cache key
        cache_key = f"geocode:{address}:{city}:{state}".replace(" ", "_").lower()
        
        # Check cache first
        cached_result = self.get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Build query string
        query = f"{address}, {city}, {state}, USA"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        'q': query,
                        'format': 'json',
                        'limit': 1,
                        'countrycodes': 'us'
                    },
                    headers={'User-Agent': self.user_agent},
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    result = (lat, lon)
                    
                    # Cache the result for 24 hours
                    self.set_cache(cache_key, result, 86400)
                    return result
                    
        except Exception as e:
            self.log_error(f"Geocoding error for {query}", e)
            
        return None
    
    async def geocode_fuel_stations(self, stations: List[FuelStation]) -> List[FuelStation]:
        """
        Geocode multiple fuel stations with rate limiting
        Only geocodes stations that haven't been geocoded yet
        """
        stations_to_geocode = [s for s in stations if not s.geocoded]
        
        if not stations_to_geocode:
            return stations
            
        geocoded_stations = []
        
        for i, station in enumerate(stations_to_geocode):
            try:
                coords = await self.geocode_address(
                    station.address, 
                    station.city, 
                    station.state
                )
                
                if coords:
                    station.latitude = coords[0]
                    station.longitude = coords[1]
                    station.geocoded = True
                    await sync_to_async(station.save)()
                    geocoded_stations.append(station)
                else:
                    geocoded_stations.append(station)
                    
                # Rate limiting - wait between requests
                if i < len(stations_to_geocode) - 1:
                    await asyncio.sleep(self.rate_limit_delay)
                    
            except Exception as e:
                self.log_error(f"Error geocoding station {station.name}", e)
                geocoded_stations.append(station)
        
        return geocoded_stations
    
    def geocode_sync(self, address: str, city: str, state: str) -> Optional[Tuple[float, float]]:
        """
        Synchronous wrapper for geocoding
        """
        return asyncio.run(self.geocode_address(address, city, state))
