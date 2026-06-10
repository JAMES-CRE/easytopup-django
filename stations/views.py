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

    def create(self, request, *args, **kwargs):
        """Create station with premium data support"""
        data = request.data.copy()
        
        # Convert frontend premium format to backend format
        # Petrol data
        if 'petrol' in data:
            data['petrol_data'] = {'petrol': data.pop('petrol')}
        
        # Diesel data
        if 'diesel' in data:
            data['diesel_data'] = {'diesel': data.pop('diesel')}
        
        # EV data
        if 'charging_points' in data:
            ev_data = {
                'charging_points': data.pop('charging_points'),
                'has_backup_generator': data.pop('has_backup_generator', False)
            }
            data['ev_data'] = ev_data
        
        # Handle LPG price (keep simple)
        # No transformation needed - keep as is
        
        # Set operator and default values
        data['operator'] = request.user.id
        data['status'] = 'Open'
        data['verified'] = False
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def update(self, request, *args, **kwargs):
        """Update station with premium data support"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        
        # Convert frontend premium format to backend format for update
        if 'petrol' in data:
            data['petrol_data'] = {'petrol': data.pop('petrol')}
        
        if 'diesel' in data:
            data['diesel_data'] = {'diesel': data.pop('diesel')}
        
        if 'charging_points' in data:
            ev_data = {
                'charging_points': data.pop('charging_points'),
                'has_backup_generator': data.pop('has_backup_generator', instance.has_backup_generator)
            }
            data['ev_data'] = ev_data
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    


        def retrieve(self, request, *args, **kwargs):
            """Get station with premium data transformed for Flutter"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Transform backend format to frontend format
        # Petrol data
        if data.get('petrol_data'):
            petrol_data = data['petrol_data']
            if 'petrol' in petrol_data:
                data['petrol'] = petrol_data['petrol']
            if 'diesel' in petrol_data:
                data['diesel'] = petrol_data['diesel']
            del data['petrol_data']
        
        # EV data
        if data.get('ev_data'):
            ev_data = data['ev_data']
            data['charging_points'] = ev_data.get('charging_points', [])
            data['has_backup_generator'] = ev_data.get('has_backup_generator', False)
            del data['ev_data']
        
        return Response(data)

        def retrieve(self, request, *args, **kwargs):
            """Get station with premium data transformed for Flutter"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Transform backend format to frontend format
        # Petrol data
        if data.get('petrol_data'):
            petrol_data = data['petrol_data']
            if 'petrol' in petrol_data:
                data['petrol'] = petrol_data['petrol']
            if 'diesel' in petrol_data:
                data['diesel'] = petrol_data['diesel']
            del data['petrol_data']
        
        # EV data
        if data.get('ev_data'):
            ev_data = data['ev_data']
            data['charging_points'] = ev_data.get('charging_points', [])
            data['has_backup_generator'] = ev_data.get('has_backup_generator', False)
            del data['ev_data']
        
        return Response(data)   
    
        def list(self, request, *args, **kwargs):
            """List stations with premium data transformed for Flutter"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            # Transform each station
            for item in data:
                self._transform_premium_data(item)
            return self.get_paginated_response(data)
        
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for item in data:
            self._transform_premium_data(item)
        return Response(data)
    
    def _transform_premium_data(self, data):
        """Helper method to transform premium data for Flutter"""
        if data.get('petrol_data'):
            petrol_data = data['petrol_data']
            if 'petrol' in petrol_data:
                data['petrol'] = petrol_data['petrol']
            if 'diesel' in petrol_data:
                data['diesel'] = petrol_data['diesel']
            del data['petrol_data']
        
        if data.get('ev_data'):
            ev_data = data['ev_data']
            data['charging_points'] = ev_data.get('charging_points', [])
            data['has_backup_generator'] = ev_data.get('has_backup_generator', False)
            del data['ev_data']
        
        return data
        