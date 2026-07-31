from django.db import models
from django.conf import settings
from stations.models import Station

class Report(models.Model):
    ISSUE_TYPES = (
        ('unusual_price', 'Unusual Price'),
        ('poor_quality', 'Poor Fuel Quality'),
        ('fuel_shortage', 'Fuel Shortage'),
        ('charger_not_working', 'Charger Not Working'),
        ('wrong_connector', 'Wrong Connector Type'),
        ('slow_charging', 'Slow Charging Speed'),
        ('price_higher', 'Price Higher Than Listed'),
        ('damaged_charger', 'Charger Damaged/Vandalized'),
        ('stopped_unexpectedly', 'Charging Stopped Unexpectedly'),
        ('no_backup', 'No Backup Generator'),
        ('leakage', 'Suspected Gas Leakage'),
        ('underfilling', 'Underfilling of Cylinders'),
        ('long_queue', 'Long Queue'),
        ('slow_service', 'Slow Refill Service'),
        ('cylinder_not_available', 'Cylinder Size Not Available'),
        ('other', 'Other'),
    )

    # ─── ADDED STATUS CHOICES ───
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    )

    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES)
    extra_data = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, default='')
    photo_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # ─── NEW REPLY FIELDS ───
    operator_reply = models.TextField(blank=True, null=True)
    reply_created_at = models.DateTimeField(blank=True, null=True)
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replied_reports'
    )

    def __str__(self):
        return f"{self.user.email} - {self.station.name} - {self.issue_type}"

    @property
    def has_reply(self):
        return self.operator_reply is not None and self.operator_reply != ''


class Review(models.Model):
    """User reviews/ratings for stations"""
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(help_text="Rating from 1 to 5 stars")
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Show newest reviews first
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.user.email} - {self.station.name} - {self.rating}★"