#create your models here.
from django.db import models
from django.contrib.postgres.fields import ArrayField
from users.models import User
import uuid

class Station(models.Model):
    FUEL_TYPES = (
        ('Petrol/Diesel', 'Petrol/Diesel'),
        ('LPG', 'LPG'),
        ('EV', 'EV'),
    )

    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    )

    #id = models.CharField(max_length=30, primary_key=True)
    id = models.CharField(max_length=30, primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=FUEL_TYPES)
    lat = models.FloatField()
    lng = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    price = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)

    # Petrol/Diesel specific
    octane = models.CharField(max_length=20, blank=True, null=True)

    # EV specific
    connector = models.CharField(max_length=20, blank=True, null=True)
    power_output = models.CharField(max_length=20, blank=True, null=True)
    has_backup_generator = models.BooleanField(default=False)

    # LPG specific - use JSONField instead of ArrayField for SQLite compatibility
    lpg_type = models.JSONField(default=list, blank=True, null=True)
    lpg_price_per_kg = models.FloatField(blank=True, null=True)
    delivery_available = models.BooleanField(default=False)

    # Common fields - use JSONField instead of ArrayField
    photos = models.JSONField(default=list, blank=True)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stations')
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def cylinder_prices(self):
        """Calculate cylinder prices for LPG stations"""
        if self.type == 'LPG' and self.lpg_price_per_kg:
            per_kg = self.lpg_price_per_kg
            return {
                '3kg': f'GH₵ {per_kg * 3:.2f}',
                '6kg': f'GH₵ {per_kg * 6:.2f}',
                '11kg': f'GH₵ {per_kg * 11:.2f}',
                '14.5kg': f'GH₵ {per_kg * 14.5:.2f}',
                '15kg': f'GH₵ {per_kg * 15:.2f}',
                '50kg': f'GH₵ {per_kg * 50:.2f}',
            }
        return None