from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from ..models.Appointment import Appointment
from ..serializers.Appointment import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by('-scheduled_time')
    serializer_class = AppointmentSerializer
    search_fields = ['description', 'status', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['scheduled_time', 'created_at']
    filterset_fields = ['status', 'customer']

    def get_queryset(self):
        """
        Enhanced queryset with filtering
        """
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming appointments
        """
        upcoming_appointments = self.get_queryset().filter(
            scheduled_time__gte=timezone.now(),
            status='SCHEDULED'
        )
        serializer = self.get_serializer(upcoming_appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Get today's appointments
        """
        today = timezone.now().date()
        today_appointments = self.get_queryset().filter(
            scheduled_time__date=today
        )
        serializer = self.get_serializer(today_appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark appointment as completed
        """
        appointment = self.get_object()
        appointment.status = 'COMPLETED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an appointment
        """
        appointment = self.get_object()
        appointment.status = 'CANCELLED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """
        Delete all appointments (for testing)
        """
        Appointment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
