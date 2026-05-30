from django.urls import path, include
from .views import upload_photos, upload_profile_photo

urlpatterns = [
    path('users/', include('users.urls')),
    path('stations/', include('stations.urls')),
    path('reports/', include('reports.urls')),
    # Photo upload endpoints (matching Flutter)
    path('upload/', upload_photos, name='upload_photos'),
    path('upload/profile/', upload_profile_photo, name='upload_profile_photo'),
]