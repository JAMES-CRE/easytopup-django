from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Report, Review
from .serializers import ReportSerializer, ReviewSerializer
from stations.models import Station


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Report.objects.all()

        # Filter by station if provided (for operators viewing station reports)
        station_id = self.request.query_params.get('station', None)
        if station_id:
            return queryset.filter(station_id=station_id)

        # Role-based filtering
        if user.role == 'admin':
            return queryset
        return queryset.filter(user=user)

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

    # REPLY TO REPORT
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        """Operator replies to a report"""
        try:
            # Get the report directly by ID
            report = Report.objects.get(id=pk)
        except Report.DoesNotExist:
            return Response(
                {'error': 'Report not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        # Only station operator or admin can reply
        if report.station.operator != user and user.role != 'admin':
            return Response(
                {'error': 'You do not have permission to reply to this report.'},
                status=status.HTTP_403_FORBIDDEN
            )

        reply_text = request.data.get('reply')
        if not reply_text or len(reply_text.strip()) < 2:
            return Response(
                {'error': 'Reply must be at least 2 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update report with reply and mark as resolved
        report.operator_reply = reply_text.strip()
        report.reply_created_at = timezone.now()
        report.replied_by = user
        report.status = 'resolved'

        report.save()

        return Response({
            'success': True,
            'message': 'Reply sent successfully.',
            'data': ReportSerializer(report).data
        })

    #  OPERATOR REPORTS
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def operator_reports(self, request):
        """Get all reports for stations owned by the operator"""
        user = request.user

        if user.role not in ['operator', 'admin']:
            return Response(
                {'error': 'Access denied. Only operators can view this data.'},
                status=status.HTTP_403_FORBIDDEN
            )

        stations = Station.objects.filter(operator=user)

        if not stations.exists():
            return Response([])

        reports = Report.objects.filter(station__in=stations).order_by('-created_at')

        serializer = ReportSerializer(reports, many=True)
        data = serializer.data

        for item, report in zip(data, reports):
            item['station_name'] = report.station.name if report.station else 'Unknown'
            item['user_name'] = report.user.email if report.user else 'Anonymous'

        return Response(data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        station_id = self.request.query_params.get('station', None)
        if station_id:
            queryset = queryset.filter(station_id=station_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)