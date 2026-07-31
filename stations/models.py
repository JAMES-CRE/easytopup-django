from django.db import models
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

    # ID
    id = models.CharField(
        max_length=36,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # BASIC FIELDS
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=FUEL_TYPES)
    lat = models.FloatField()
    lng = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Open',
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    price = models.CharField(max_length=50, blank=True, null=True)
    photos = models.JSONField(default=list, blank=True)

    # EV
    has_backup_generator = models.BooleanField(default=False)
    ev_data = models.JSONField(default=list, blank=True, null=True)

    # LPG
    lpg_type = models.JSONField(default=list, blank=True, null=True)
    delivery_available = models.BooleanField(default=False)

    # PETROL/DIESEL
    petrol_data = models.JSONField(default=dict, blank=True, null=True)
    diesel_data = models.JSONField(default=dict, blank=True, null=True)

    # RELATIONS
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stations',
    )

    # APPROVAL
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']