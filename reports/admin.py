<<<<<<< Updated upstream
from django.contrib import admin
from .models import Report, Review

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'user', 'issue_type', 'status', 'created_at')
    list_filter = ('issue_type', 'status')
    search_fields = ('station__name', 'user__email')
    readonly_fields = ('created_at',)

  

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'user', 'rating', 'comment', 'created_at')
    list_filter = ('rating',)
    search_fields = ('station__name', 'user__email', 'comment')
