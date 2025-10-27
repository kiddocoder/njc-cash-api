from rest_framework import viewsets
from ..models.Appointment import Appointment
from ..serializers.Appointment import AppointmentSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by('-scheduled_time')
    serializer_class = AppointmentSerializer
    search_fields = ['description', 'status']
    ordering_fields = ['scheduled_time', 'created_at']

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Appointment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)