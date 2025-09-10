"""
Utility functions for the planner app
"""
import math
from typing import List, Tuple


def decode_polyline(polyline: str) -> List[Tuple[float, float]]:
    """
    Decode a polyline string into a list of [lon, lat] coordinate pairs.
    
    Args:
        polyline: The encoded polyline string
        
    Returns:
        List of (longitude, latitude) tuples
    """
    if not polyline:
        return []
    
    # Index into the array
    index = 0
    lat = 0
    lng = 0
    coordinates = []
    
    while index < len(polyline):
        # Get the next coordinate
        shift = 0
        result = 0
        b = 0
        
        while True:
            b = ord(polyline[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        
        # Check for negative value
        if result & 1:
            result = ~(result >> 1)
        else:
            result = result >> 1
        
        # Add to the coordinate
        lat += result
        
        # Get the next coordinate
        shift = 0
        result = 0
        b = 0
        
        while True:
            b = ord(polyline[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        
        # Check for negative value
        if result & 1:
            result = ~(result >> 1)
        else:
            result = result >> 1
        
        # Add to the coordinate
        lng += result
        
        # Add the coordinate pair
        coordinates.append((lng, lat))
    
    return coordinates


def coordinates_to_geojson_line_string(coordinates: List[Tuple[float, float]]) -> dict:
    """
    Convert a list of coordinate pairs to GeoJSON LineString format.
    
    Args:
        coordinates: List of (longitude, latitude) tuples
        
    Returns:
        GeoJSON LineString object
    """
    return {
        "type": "LineString",
        "coordinates": coordinates
    }


def polyline_to_geojson(polyline: str) -> dict:
    """
    Convert a polyline string directly to GeoJSON LineString format.
    
    Args:
        polyline: The encoded polyline string
        
    Returns:
        GeoJSON LineString object
    """
    coordinates = decode_polyline(polyline)
    return coordinates_to_geojson_line_string(coordinates)
