# Spotter Route API

A Django API for route planning with optimal fuel stops using real fuel station data.

## Quick Start

```bash
# Start everything
make setup

# Or quick start (without geocoding all stations)
make quick-start
```

## API Usage

### POST /api/route-plan/

**Input:**
```json
{
  "start": "New York, NY",
  "finish": "Chicago, IL"
}
```

**Output:**
```json
{
  "summary": {
    "start": {"location": "New York, NY", "coordinates": {"lat": 40.7128, "lon": -74.0060}},
    "finish": {"location": "Chicago, IL", "coordinates": {"lat": 41.8781, "lon": -87.6298}},
    "total_distance_miles": 789.2,
    "total_duration_hours": 12.5,
    "fuel_efficiency_mpg": 10,
    "vehicle_max_range_miles": 500,
    "total_cost": 245.67,
    "total_fuel_gallons": 78.92,
    "number_of_stops": 2
  },
  "route": {
    "geojson": {
      "type": "LineString",
      "coordinates": [[-74.0060, 40.7128], [-87.6298, 41.8781]]
    },
    "distance_meters": 1270000,
    "duration_seconds": 45000
  },
  "fuel_stops": [
    {
      "name": "7-ELEVEN #218",
      "address": "I-44, EXIT 4",
      "city": "Harrold",
      "state": "TX",
      "coordinates": {"lat": 34.938, "lon": -93.103},
      "price_per_gallon": 2.687,
      "distance_from_prev_miles": 377.36,
      "fuel_needed_gallons": 37.74,
      "cost": 101.4
    }
  ]
}
```

## Makefile Commands

```bash
# Start the application
make up

# Build and start everything
make setup

# Quick start (without geocoding)
make quick-start

# Load fuel station data
make load-data

# Geocode fuel stations
make geocode

# View logs
make logs

# Run tests
make test

# Stop everything
make down

# Clean up
make clean
```

## Features

- **Route Planning**: OSRM integration for accurate routing
- **Fuel Optimization**: Real fuel station data with actual prices
- **GeoJSON Support**: Standard LineString format for frontend mapping
- **Caching**: Redis-based caching for fast responses
- **Docker**: Fully containerized with PostgreSQL and Redis

## Next Steps

1. **Start the API**: `make setup`
2. **Test the API**: `curl -X POST http://localhost:8000/api/route-plan/ -H "Content-Type: application/json" -d '{"start": "New York, NY", "finish": "Chicago, IL"}'`
3. **View logs**: `make logs`
4. **Stop when done**: `make down`