import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from planner.models import FuelStation


class Command(BaseCommand):
    help = 'Load fuel stations from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/fuel-prices-for-be-assessment.csv',
            help='Path to the CSV file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing fuel stations before loading'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
            return

        if options['clear']:
            self.stdout.write('Clearing existing fuel stations...')
            FuelStation.objects.all().delete()

        self.stdout.write(f'Loading fuel stations from {file_path}...')
        
        created_count = 0
        updated_count = 0
        error_count = 0

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
                    try:
                        # Parse the data
                        opis_id = int(row['OPIS Truckstop ID'])
                        name = row['Truckstop Name'].strip()
                        city = row['City'].strip()
                        address = row['Address'].strip()
                        state = row['State'].strip()
                        rack_id = int(row['Rack ID'])
                        retail_price = float(row['Retail Price'])

                        # Create or update the fuel station
                        station, created = FuelStation.objects.update_or_create(
                            opis_id=opis_id,
                            defaults={
                                'name': name,
                                'city': city,
                                'address': address,
                                'state': state,
                                'rack_id': rack_id,
                                'retail_price': retail_price,
                            }
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                        if row_num % 1000 == 0:
                            self.stdout.write(f'Processed {row_num} rows...')

                    except (ValueError, KeyError) as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Error on row {row_num}: {e}')
                        )
                        continue

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded fuel stations!\n'
                f'Created: {created_count}\n'
                f'Updated: {updated_count}\n'
                f'Errors: {error_count}'
            )
        )
