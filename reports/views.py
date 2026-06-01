from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Report, Review
from .serializers import ReportSerializer, ReviewSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Report.objects.all()
        return Report.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Report submitted successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class ReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for station reviews"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filter reviews by station if station_id is provided"""
        queryset = Review.objects.all()
        station_id = self.request.query_params.get('station', None)
        if station_id:
            queryset = queryset.filter(station_id=station_id)
        return queryset
    
    def perform_create(self, serializer):
        """Automatically set the user to the logged-in user"""
        serializer.save(user=self.request.user)