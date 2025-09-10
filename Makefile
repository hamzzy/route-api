.PHONY: build up down logs shell migrate load-data geocode test clean

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f web

shell:
	docker-compose exec web python manage.py shell

# Database commands
migrate:
	docker-compose exec web python manage.py migrate

# Data loading commands
load-data:
	docker-compose exec web python manage.py load_fuel_stations

geocode:
	docker-compose exec web python manage.py geocode_stations --limit 1000

# Development commands
test:
	docker-compose exec web python manage.py test

test-api:
	docker-compose exec web python manage.py test_api

test-api-local:
	python manage.py test_api

clean:
	docker-compose down -v
	docker system prune -f

# Full setup
setup: build up migrate load-data geocode
	@echo "Setup complete! API available at http://localhost:8000/api/route-plan/"

# Quick start (without geocoding all stations)
quick-start: build up migrate load-data
	@echo "Quick start complete! API available at http://localhost:8000/api/route-plan/"
	@echo "Run 'make geocode' to geocode fuel stations for better results"