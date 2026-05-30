# stations/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Station
from .serializers import StationSerializer

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'status', 'verified']
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']
    
    def get_queryset(self):
        user = self.request.user
        # Public users see only verified stations
        if not user.is_authenticated:
            return Station.objects.filter(verified=True)
        # Admin sees all stations
        if user.role == 'admin':
            return Station.objects.all()
        # Operators see their own stations
        if user.role == 'operator':
            return Station.objects.filter(operator=user)
        # Regular users see only verified stations
        return Station.objects.filter(verified=True)
    
    # ─────────────────────────────────────────────
    # OPERATOR SPECIFIC ENDPOINTS
    # ─────────────────────────────────────────────
    
    @action(detail=False, methods=['get'], url_path='my-stations')
    def my_stations(self, request):
        """Get stations owned by the logged-in operator"""
        stations = Station.objects.filter(operator=request.user)
        serializer = self.get_serializer(stations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='update-price')
    def update_price(self, request, pk=None):
        """Update station price"""
        station = self.get_object()
        
        # Check permission: only operator who owns it or admin
        if request.user.role != 'admin' and station.operator != request.user:
            return Response(
                {'error': 'You do not have permission to update this station'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        price = request.data.get('price')
        if not price:
            return Response(
                {'error': 'Price is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        station.price = price
        station.save()
        
        return Response({
            'success': True,
            'message': 'Price updated successfully',
            'price': station.price
        })
    
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        """Update station status (Open/Closed)"""
        station = self.get_object()
        
        if request.user.role != 'admin' and station.operator != request.user:
            return Response(
                {'error': 'You do not have permission to update this station'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        status_value = request.data.get('status')
        if not status_value:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status choice
        if status_value not in ['Open', 'Closed']:
            return Response(
                {'error': 'Status must be "Open" or "Closed"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        station.status = status_value
        station.save()
        
        return Response({
            'success': True,
            'message': f'Station marked as {status_value}',
            'status': station.status
        })
    
    @action(detail=True, methods=['post'], url_path='update-power')
    def update_power(self, request, pk=None):
        """Update power output (EV only)"""
        station = self.get_object()
        
        if request.user.role != 'admin' and station.operator != request.user:
            return Response(
                {'error': 'You do not have permission to update this station'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if station.type != 'EV':
            return Response(
                {'error': 'Power output only applicable to EV stations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        power_output = request.data.get('power_output')
        if not power_output:
            return Response(
                {'error': 'Power output is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        station.power_output = power_output
        station.save()
        
        return Response({
            'success': True,
            'message': 'Power output updated successfully',
            'power_output': station.power_output
        })
    
    # ─────────────────────────────────────────────
    # ADMIN SPECIFIC ENDPOINTS
    # ─────────────────────────────────────────────
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending_stations(self, request):
        """Get all unverified stations (admin only)"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stations = Station.objects.filter(verified=False)
        serializer = self.get_serializer(stations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_station(self, request, pk=None):
        """Approve a station (admin only)"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        station = self.get_object()
        station.verified = True
        station.save()
        
        return Response({
            'success': True,
            'message': f'Station "{station.name}" has been approved'
        })
    
    def perform_create(self, serializer):
        """Automatically set operator to logged-in user and status to Open"""
        serializer.save(
            operator=self.request.user,
            status='Open',
            verified=False
        )