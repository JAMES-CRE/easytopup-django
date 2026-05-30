from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Station

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'status', 'verified', 'operator')
    list_filter = ('type', 'status', 'verified')
    search_fields = ('name', 'id')
    readonly_fields = ('created_at',)