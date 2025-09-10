from django.db import models


class FuelStation(models.Model):
    """Model for fuel stations with pricing and location data"""
    opis_id = models.IntegerField(unique=True, help_text="OPIS Truckstop ID")
    name = models.CharField(max_length=255, help_text="Truckstop Name")
    address = models.TextField(help_text="Full address")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    rack_id = models.IntegerField(help_text="Rack ID")
    retail_price = models.DecimalField(max_digits=6, decimal_places=3, help_text="Retail price per gallon")
    
    # Location fields - will be populated by geocoding
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    geocoded = models.BooleanField(default=False, help_text="Whether this station has been geocoded")
    
    class Meta:
        ordering = ['retail_price']
        indexes = [
            models.Index(fields=['state', 'retail_price']),
            models.Index(fields=['geocoded']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.state} - ${self.retail_price}"
