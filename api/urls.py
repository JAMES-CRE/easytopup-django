from django.urls import path, include

urlpatterns = [
    path('users/', include('users.urls')),
    path('stations/', include('stations.urls')),
    path('reports/', include('reports.urls')),

]