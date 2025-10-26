# customer view set

from rest_framework import viewsets
from ..models.Customer import Customer
from ..serializers.Customer import CustomerSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['created_at', 'first_name']

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Customer.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)