from rest_framework import viewsets
from ..models.Loan import Loan
from ..serializers.Loan import LoanSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all().order_by('-created_at')
    serializer_class = LoanSerializer
    search_fields = ['customer__first_name', 'customer__last_name', 'status']
    ordering_fields = ['created_at', 'amount']

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Loan.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)