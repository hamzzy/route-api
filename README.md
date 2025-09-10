# Spotter Route API

A Django 3.2.23 API for route planning with optimal fuel stops based on real-time fuel prices.

## Features

- **Route Planning**: Uses OSRM for accurate routing between any two US locations
- **Fuel Optimization**: Finds the most cost-effective fuel stops along the route
- **Real-time Pricing**: Uses actual fuel station data with current prices
- **Caching**: Redis-based caching for fast response times
- **Geocoding**: Automatic geocoding of fuel stations with caching
- **Docker Support**: Fully containerized with PostgreSQL and Redis
- **Django Best Practices**: Class-based views, serializers, proper error handling
- **Comprehensive Testing**: Unit tests, integration tests, and API tests
- **API Documentation**: Built-in API documentation endpoint
- **Logging**: Structured logging for monitoring and debugging

## Services Architecture

The API uses a clean service layer architecture with the following services:

### Core Services

- **`RoutePlanningService`** (`planner/services/routing.py`)
  - Handles route planning using OSRM API
  - Geocodes start/finish locations using Nominatim
  - Returns route geometry, distance, and duration

- **`HybridFuelOptimizationService`** (`planner/services/hybrid_fuel_optimization.py`)
  - Optimizes fuel stops using real fuel station data
  - Uses actual fuel prices from the database
  - Places fuel stops along the route at optimal intervals
  - Balances cost-effectiveness with route efficiency

- **`GeocodingService`** (`planner/services/geocoding.py`)
  - Geocodes addresses to coordinates using Nominatim
  - Implements rate limiting and caching
  - Stores geocoded results in the database for reuse

- **`BaseService`** (`planner/services/base.py`)
  - Base class for all services
  - Provides common functionality like logging and error handling

## API Endpoint

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
    "start": {
      "location": "New York, NY",
      "coordinates": {"lat": 40.7128, "lon": -74.0060}
    },
    "finish": {
      "location": "Chicago, IL", 
      "coordinates": {"lat": 41.8781, "lon": -87.6298}
    },
    "total_distance_miles": 789.2,
    "total_duration_hours": 12.5,
    "fuel_efficiency_mpg": 10,
    "vehicle_max_range_miles": 500,
    "total_cost": 245.67,
    "total_fuel_gallons": 78.92,
    "number_of_stops": 2
  },
  "route": {
    "geometry": "encoded_polyline_string",
    "distance_meters": 1270000,
    "duration_seconds": 45000
  },
  "fuel_stops": [
    {
      "station": {
        "id": 123,
        "name": "PILOT TRAVEL CENTER",
        "address": "I-80, EXIT 123",
        "city": "Cleveland",
        "state": "OH",
        "price": 3.25,
        "coordinates": {"lat": 41.4993, "lon": -81.6944}
      },
      "distance_from_previous": 450.2,
      "fuel_needed": 45.02,
      "cost": 146.32
    }
  ]
}
```

## Setup Instructions

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd spotter_route_api
   ```

2. **Create environment file:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services:**
   ```bash
   docker-compose up --build
   ```

4. **Load fuel station data:**
   ```bash
   docker-compose exec web python manage.py load_fuel_stations
   ```

5. **Geocode fuel stations:**
   ```bash
   docker-compose exec web python manage.py geocode_stations --limit 1000
   ```

6. **Access the API:**
   - API: http://localhost:8000/api/route-plan/
   - Admin: http://localhost:8000/admin/

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL with PostGIS:**
   ```bash
   # Install PostgreSQL and PostGIS
   # Create database: spotter_route
   ```

3. **Set up Redis:**
   ```bash
   # Install and start Redis server
   ```

4. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your database and Redis URLs
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Load data:**
   ```bash
   python manage.py load_fuel_stations
   python manage.py geocode_stations --limit 1000
   ```

7. **Start server:**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Environment Variables

- `DEBUG`: Django debug mode (True/False)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Django secret key
- `NOMINATIM_USER_AGENT`: User agent for geocoding requests
- `OSRM_BASE_URL`: OSRM routing service URL

### Vehicle Configuration

- **Fuel Efficiency**: 10 MPG (configurable in settings)
- **Maximum Range**: 500 miles (configurable in settings)
- **Cache TTL**: 1 hour (configurable in settings)

## Management Commands

### Load Fuel Stations
```bash
python manage.py load_fuel_stations --file data/fuel-prices-for-be-assessment.csv
```

### Geocode Stations
```bash
python manage.py geocode_stations --limit 1000 --batch-size 10
```

## API Usage Examples

### cURL
```bash
curl -X POST http://localhost:8000/api/route-plan/ \
  -H "Content-Type: application/json" \
  -d '{"start": "New York, NY", "finish": "Los Angeles, CA"}'
```

### Python
```python
import requests

response = requests.post(
    'http://localhost:8000/api/route-plan/',
    json={
        'start': 'New York, NY',
        'finish': 'Los Angeles, CA'
    }
)
data = response.json()
print(f"Total cost: ${data['summary']['total_cost']}")
```

## Performance

- **Caching**: All route responses are cached for 1 hour
- **Geocoding**: Only geocodes stations that are actually used
- **Rate Limiting**: Respects Nominatim's 1 request/second limit
- **Async Processing**: Uses asyncio for concurrent API calls

## Architecture

- **Django 3.2.23**: Web framework
- **PostgreSQL + PostGIS**: Database with spatial support
- **Redis**: Caching layer
- **OSRM**: Open-source routing engine
- **Nominatim**: OpenStreetMap geocoding service

## Development

### Running Tests
```bash
# Run all tests
python manage.py test

# Run tests with coverage
pytest --cov=planner

# Test the API
python manage.py test_api
```

### Code Quality
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Format code
black .

# Lint code
flake8 .

# Sort imports
isort .

# Type checking
mypy .
```

### API Testing
```bash
# Test API locally
make test-api-local

# Test API in Docker
make test-api

# Test specific route
python manage.py test_api --start "New York, NY" --finish "Los Angeles, CA"
```

## License

This project is licensed under the MIT License.
