from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Station
from .serializers import StationSerializer


class StationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for stations
    - Public: list (verified only) and retrieve
    - Authenticated: create, update, delete
    - Operators: can manage their own stations
    - Admins: can approve stations
    """

    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_permissions(self):
        """Public can view, authenticated can modify"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Public only sees verified stations"""
        if self.action == 'list':
            return Station.objects.filter(verified=True)
        return Station.objects.all()

    #  CREATE
    def create(self, request, *args, **kwargs):
        """Operator creates a new station (pending approval)"""
        # Only operators and admins can add stations
        if request.user.role not in ['operator', 'admin']:
            return Response(
                {'error': 'Only operators can add stations'},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()

        print("=== DJANGO CREATE ===")
        print(f"Raw data: {data}")

        # CONVERT FLUTTER FIELD NAMES TO BACKEND FIELD NAMES
        if 'petrol' in data:
            data['petrol_data'] = data.pop('petrol')
        if 'diesel' in data:
            data['diesel_data'] = data.pop('diesel')
        if 'charging_points' in data:
            data['ev_data'] = data.pop('charging_points')

        # SET OPERATOR AND DEFAULTS
        data['operator'] = request.user.id
        data['status'] = 'Open'
        data['verified'] = False

        print(f"Converted data: {data}")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # READ
    @action(detail=False, methods=['get'],
            url_path='my-stations', permission_classes=[IsAuthenticated])
    def my_stations(self, request):
        """Get stations owned by the logged-in operator"""
        stations = Station.objects.filter(operator=request.user)
        serializer = StationSerializer(stations, many=True)
        return Response(serializer.data)

    #  UPDATE
    def update(self, request, *args, **kwargs):
        """Full station update (operators edit their stations)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        print("=== DJANGO UPDATE ===")
        print(f"Raw data: {data}")
        print(f"Instance before: {instance.name}")

        # CHECK PERMISSIONS
        if instance.operator != request.user and request.user.role != 'admin':
            return Response(
                {'error': 'Not authorized to edit this station'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # DIRECT FIELD UPDATE
        # Handle EV charging points
        if 'charging_points' in data:
            instance.ev_data = data.pop('charging_points')
            print(f"EV data updated: {instance.ev_data}")

        # Handle Petrol/Diesel
        if 'petrol' in data:
            instance.petrol_data = data.pop('petrol')
        if 'diesel' in data:
            instance.diesel_data = data.pop('diesel')

        # Handle basic fields
        for key in ['name', 'phone', 'whatsapp', 'lat', 'lng', 'photos',
                    'has_backup_generator', 'price', 'status', 'lpg_type',
                    'delivery_available']:
            if key in data:
                setattr(instance, key, data[key])

        # Save the instance
        instance.save()

        print(f"Instance after: {instance.name}")
        print(f"EV data after save: {instance.ev_data}")

        # Return the updated data using the serializer
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # UPDATE STATUS
    @action(detail=True, methods=['post'],
            url_path='update-status', permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """Quick status update (Open/Closed) without full edit"""
        station = self.get_object()

        if station.operator != request.user and request.user.role != 'admin':
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN,
            )

        new_status = request.data.get('status')
        if not new_status or new_status not in ['Open', 'Closed']:
            return Response(
                {'error': 'Status must be Open or Closed'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        station.status = new_status
        station.save()
        return Response({'message': f'Station marked as {new_status}'})

    # ADMIN ACTIONS
    @action(detail=True, methods=['post'],
            url_path='approve', permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Admin approves a pending station"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin only'},
                status=status.HTTP_403_FORBIDDEN,
            )

        station = self.get_object()
        station.verified = True
        station.save()
        return Response({'message': 'Station approved successfully'})

    #  HELPER
    def perform_create(self, serializer):
        """Set default values when creating a station"""
        serializer.save(
            operator=self.request.user,
            status='Open',
            verified=False
        )