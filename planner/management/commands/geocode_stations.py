import asyncio
from django.core.management.base import BaseCommand
from django.db import transaction
from planner.models import FuelStation
from planner.services.geocoding import GeocodingService


class Command(BaseCommand):
    help = 'Geocode fuel stations that haven\'t been geocoded yet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of stations to geocode in this run'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of stations to process in each batch'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        batch_size = options['batch_size']
        
        # Get stations that need geocoding
        stations_to_geocode = FuelStation.objects.filter(
            geocoded=False
        )[:limit]
        
        total_stations = stations_to_geocode.count()
        
        if total_stations == 0:
            self.stdout.write(
                self.style.SUCCESS('No stations need geocoding!')
            )
            return
        
        self.stdout.write(f'Found {total_stations} stations to geocode...')
        
        # Process in batches
        geocoding_service = GeocodingService()
        processed = 0
        geocoded = 0
        
        for i in range(0, total_stations, batch_size):
            batch = stations_to_geocode[i:i + batch_size]
            
            self.stdout.write(f'Processing batch {i//batch_size + 1}...')
            
            # Geocode the batch
            geocoded_batch = asyncio.run(
                geocoding_service.geocode_fuel_stations(list(batch))
            )
            
            # Count successful geocodings
            batch_geocoded = sum(1 for station in geocoded_batch if station.geocoded)
            geocoded += batch_geocoded
            processed += len(batch)
            
            self.stdout.write(
                f'Batch completed: {batch_geocoded}/{len(batch)} geocoded successfully'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Geocoding completed!\n'
                f'Total processed: {processed}\n'
                f'Successfully geocoded: {geocoded}\n'
                f'Success rate: {geocoded/processed*100:.1f}%'
            )
        )
